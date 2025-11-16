# Roadmap

1. Add the Anki Backend, and a very basic UI (through AnkiConnect)
2. Pull Board Style Questions/Explanation/Answers from PeerPrep and MKSAP19

   3. Display in terminal - First in Raw HTML
   4. Then Cleaned version (human readable)
3. Add functionality to determine whether or not the question was answered right or wrong
4. Implement persistence layer (SQLite or DuckDB prototype).
5. Display the question and answers/Explanation in a PyQt UI
6. Build interactive notebook for notes and learning points (Similar to Obsidian, or other Microsoft Notebook) that is able to be opened on a persistent floating window

   1. Note: Utilize programs that are already out there and open source, rather than reinventing the wheel
7. Normalize the Headings/Subjects in the Notebook
8. Add duplicate detection service + tests.
9. Link Question/Answer/Explanation to board topics (ABIM/ABEM taken from the .txt files obtained online)
10. Build the Learning Pipeline and transfer it to the UI

    1. Elaborative Interrogation & Self Explanation
    2. Multi Modal Reinforcement (Visuals and further examples to reinforce concepts, LLM driven)\
    3. Active Recall Practice
    4. (Optional) - Integrate related Concepts
    5. Peer Discussion/Teach an LLM "Student" about the subject
    6. (Optional) brief mini game for engagement to reinforce concept and final quiz
    7. 
11. Polish the UI

    1. Improve upon Anki (Use anki for the backend so you get the customization, but looks much better like other flashcard apps; specifically the decks, make them easier to navigate)
12. If not present, add a search function)
