# FastAPI TicTacToe Game REST API Development Project
## Objective
Design, implement, and test a FastAPI-based REST API for a TicTacToe game. 

The API should enable users to:

- Create and manage games
- Make moves
- Check win/draw conditions
- View game history

The project should demonstrate proficiency in RESTful API design, database integration, business logic, testing, and documentation.

## Requirements
**1. FastAPI REST API with User Authentication**
- Develop a FastAPI application for the TicTacToe game.
- Implement basic user handling and authentication (e.g., JWT or OAuth2).
- Ensure secure access to game endpoints.

**2. CRUD Operations for Game Management**
- Use SQLAlchemy ORM to interact with a PostgreSQL database.
- Implement CRUD operations for:
  - Creating new games
  - Updating move histories
  - Deleting completed games

**3. Business Logic**
- Implement logic to:
 - Check win conditions (rows, columns, diagonals)
 - Detect draws (all positions filled, no winner)
 - Handle invalid moves (e.g., occupied positions, out-of-bounds)

**4. API Endpoints**
- Implement the following endpoints:

  - ``/games``	**POST**	Create a new game.
  - ``/games``	**GET**	    Retrieve a list of all games, including move histories and statuses.
  - ``/games/{game_id}/move/{position}``	**PUT**	Make a move at the specified position (1–9) in the given game.
  - ``/games/{game_id}``	**GET**	Retrieve details of a specific game, including move history and status.

**5. Unit Testing**
- Write unit tests for all API endpoints using FastAPI’s testing framework or pytest.
- Test edge cases (e.g., invalid moves, authentication failures).

**6. Documentation**
- Use FastAPI’s OpenAPI/Swagger support to document the API.
- Include clear descriptions for endpoints, request/response schemas, and examples.

**7. Code Quality**
- Follow best practices for code organization, readability, and maintainability.
- Use a modular project structure (e.g., separate files for models, routes, tests).

**8. Submission**
- Submit the following:
  - Source code (GitHub repository)
  - Documentation (README, API docs)
  - Test results (coverage report, if applicable)

## Execution and Support
### Starting Point
- You may start from scratch or fork the provided [Template Repository](https://github.com/hifigraz/backend.template).
- Customize the template as needed for your implementation.

### Repository Submission
- Provide a link to your GitHub repository in the Teams assignment.

## Clarifications and Notes
- **Authentication**: Specify whether users must log in to create/join games or if games are anonymous.
- **Game State**: Define how the game state (e.g., current player, board) is stored and updated.
- **Error Handling**: Ensure clear error messages for invalid requests (e.g., “Position already taken”).
- **Testing**: Focus on both happy paths (valid moves) and edge cases (invalid moves, full board).