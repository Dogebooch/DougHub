"""Load test script for generating synthetic database data.

This script generates a large volume of synthetic questions and media records
to provide a simple load for performance evaluation and testing.
"""

import argparse
import json
import logging
import random
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from doughub.config import DATABASE_URL
from doughub.models import Base
from doughub.persistence import QuestionRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_synthetic_html(question_num: int) -> str:
    """Generate synthetic HTML content for a question.

    Args:
        question_num: Question number for content generation.

    Returns:
        HTML string.
    """
    choices = ["A", "B", "C", "D", "E"]
    return f"""
    <div class="question">
        <h3>Question {question_num}</h3>
        <p>This is synthetic question content for testing purposes.
        Consider the following clinical scenario...</p>
        <ul>
            {''.join(f'<li>{choice}. Option {choice}</li>' for choice in choices)}
        </ul>
    </div>
    """


def generate_synthetic_metadata(question_num: int) -> dict:
    """Generate synthetic metadata for a question.

    Args:
        question_num: Question number for metadata generation.

    Returns:
        Metadata dictionary.
    """
    return {
        "question_number": question_num,
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "topic": random.choice(
            ["cardiology", "pulmonology", "gastroenterology", "neurology"]
        ),
        "correct_answer": random.choice(["A", "B", "C", "D", "E"]),
        "explanation": f"Explanation for question {question_num}",
        "references": [f"Reference {i}" for i in range(random.randint(1, 3))],
    }


def load_test_database(
    database_url: str,
    num_sources: int = 5,
    num_questions: int = 10000,
    media_probability: float = 0.7,
    max_media_per_question: int = 3,
) -> None:
    """Generate synthetic data and load it into the database.

    Args:
        database_url: Database URL to connect to.
        num_sources: Number of sources to create.
        num_questions: Total number of questions to create.
        media_probability: Probability (0-1) that a question has media.
        max_media_per_question: Maximum number of media files per question.
    """
    logger.info(f"Connecting to database: {database_url}")
    engine = create_engine(database_url, echo=False)

    # Create schema if it doesn't exist
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    repo = QuestionRepository(session)

    try:
        # Create sources
        logger.info(f"Creating {num_sources} sources...")
        sources = []
        for i in range(num_sources):
            source_name = f"SyntheticSource_{i:03d}"
            source_desc = f"Synthetic source {i} for load testing"
            source = repo.get_or_create_source(source_name, source_desc)
            sources.append(source)
        repo.commit()
        logger.info(f"Created {len(sources)} sources")

        # Create questions
        logger.info(f"Creating {num_questions} questions...")
        questions_per_source = num_questions // num_sources
        question_count = 0

        for source in sources:
            for i in range(questions_per_source):
                question_key = f"Q{i:06d}"
                question_data = {
                    "source_id": source.source_id,
                    "source_question_key": question_key,
                    "raw_html": generate_synthetic_html(question_count),
                    "raw_metadata_json": json.dumps(
                        generate_synthetic_metadata(question_count)
                    ),
                    "status": random.choice(["extracted", "processed", "reviewed"]),
                }

                question = repo.add_question(question_data)

                # Add media with probability
                if random.random() < media_probability:
                    num_media = random.randint(1, max_media_per_question)
                    for media_idx in range(num_media):
                        media_data = {
                            "media_role": "image",
                            "media_type": random.choice(
                                ["question_image", "explanation_image"]
                            ),
                            "mime_type": random.choice(
                                ["image/jpeg", "image/png", "image/gif"]
                            ),
                            "relative_path": f"{source.name}/{question_key}_img{media_idx}.jpg",
                        }
                        repo.add_media_to_question(question.question_id, media_data)

                question_count += 1

                # Commit in batches for performance
                if question_count % 1000 == 0:
                    repo.commit()
                    logger.info(f"  Created {question_count} questions...")

        # Final commit
        repo.commit()
        logger.info(f"Successfully created {question_count} questions")

        # Print statistics
        all_questions = repo.get_all_questions()
        logger.info("\nFinal Statistics:")
        logger.info(f"  Total sources: {len(sources)}")
        logger.info(f"  Total questions: {len(all_questions)}")

        # Count media
        from sqlalchemy import select

        from doughub.models import Media

        stmt = select(Media)
        media_count = len(session.execute(stmt).scalars().all())
        logger.info(f"  Total media: {media_count}")

    except Exception as e:
        logger.error(f"Error during load test: {e}", exc_info=True)
        repo.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


def main() -> None:
    """Run the load test script."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic data for load testing"
    )
    parser.add_argument(
        "--database-url",
        default=DATABASE_URL,
        help=f"Database URL (default: {DATABASE_URL})",
    )
    parser.add_argument(
        "--num-sources",
        type=int,
        default=5,
        help="Number of sources to create (default: 5)",
    )
    parser.add_argument(
        "--num-questions",
        type=int,
        default=10000,
        help="Number of questions to create (default: 10000)",
    )
    parser.add_argument(
        "--media-probability",
        type=float,
        default=0.7,
        help="Probability that a question has media (default: 0.7)",
    )
    parser.add_argument(
        "--max-media",
        type=int,
        default=3,
        help="Maximum media files per question (default: 3)",
    )

    args = parser.parse_args()

    logger.info("Starting load test...")
    logger.info(f"  Database: {args.database_url}")
    logger.info(f"  Sources: {args.num_sources}")
    logger.info(f"  Questions: {args.num_questions}")
    logger.info(f"  Media probability: {args.media_probability}")
    logger.info(f"  Max media per question: {args.max_media}")

    start_time = datetime.now()

    load_test_database(
        database_url=args.database_url,
        num_sources=args.num_sources,
        num_questions=args.num_questions,
        media_probability=args.media_probability,
        max_media_per_question=args.max_media,
    )

    elapsed = datetime.now() - start_time
    logger.info(f"\nLoad test completed in {elapsed.total_seconds():.2f} seconds")


if __name__ == "__main__":
    main()
