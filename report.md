# Short Report

## Design Decisions
- I chose Python 3 as the target language because it is widely used in teaching and supports Unicode identifiers.
- Amharic keywords were selected to reduce the English barrier for Ethiopian beginners.
- Explicit block markers (`ከዚያ` / `በቃ`) replace indentation rules, which are often confusing for new learners.

## Why This Language Helps Beginners
- Learners read instructions in their local language, which makes control flow and function definitions clearer.
- The keyword set is small and consistent, so students can focus on logic instead of syntax trivia.
- Errors are shown in Amharic, guiding students to fix mistakes without additional translation.

## Challenges
- Choosing short, clear Amharic keywords without ambiguity required careful selection.
- Ensuring Unicode identifiers and strings work correctly in the lexer and translator was essential.
- Balancing readability with minimal syntax was tricky, especially for blocks and function definitions.
