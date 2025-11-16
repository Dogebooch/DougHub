# `/review-changes` Workflow

When the user types `/review-changes`, the following pipeline is triggered.

## 1. Assumption and Hard Stops

- Assume that code changes have already been made in the working directory by the user, based on the most recent prompts or plan.md files
- DO NOT MAKE ANY CHANGES OR EDITS TO THE CODE BASE AT THIS POINT
- You can run commands, but do not make any code edits. Your job is to Audit the code base and tasks

## 2. Inputs

- The primary input is the user's command: `/review-changes`.
- The user should provide the original task, plan, or context for the changes that were made.

## 3. Workflow

1. **Inspect Changes:**

   - Run `git status` to get an overview of the modified files.
   - Run `git diff HEAD` to get the detailed changes.
   - Review the Repository to see how these changes effect the functionality of the current state of the program
2. **Summarize Effects:**

   - Analyze the output of the `git diff` to understand the modifications.
   - Provide a concise summary of what was added, removed, or changed in the codebase
3. **Provide Suggestions:**

   - Compare the changes against the provided task context.
   - Suggest further edits, improvements, or point out any missed requirements.
   - If no context is provided, the suggestions will be based on general code quality, style, and best practices.
   - It is ok to not have any suggestions if it was implemented well
   - When generating suggestions, keep in mind the end user experience

## 4. Output

- A summary of the changes.
- A list of suggestions for further action.
