
## Overview

Develop a simplified backend API using Python and FastAPI. The app will manage users.



## MySQL Structure

```
CREATE TABLE Users (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL,
password VARCHAR(255) NOT NULL
);
```
## REST API Implementation:
Develop endpoints for CRUD operations on Users.
- Implement pagination and sorting for the GET /users endpoint.
- Use classes and Pydantic models.
- Ensure proper error handling.
- Use Pydantic for validation.
- Your project should have its .env file.
- Implement pagination (with limit and offset query parameters) and sorting (by username or created_at).
- Use Pydantic for input validation.
- Use FastAPI for the server.
- Password Hashing(use passlib)
- Include error handling for common scenarios (e.g., user not found, validation errors).
## Authentication System

- Implement JWT-based authentication (pyjwt).
- Implement a login endpoint that issues a JWT token.
- Implement a dependency to protect certain endpoints using JWT.
## Role-Based Access Control (RBAC):


- Implement user roles (e.g., Admin, User).
- Restrict access to certain endpoints based on user roles.
## Dockerization

- Use Dockerfile and docker compose.
## Run Locally

Clone the project

```bash
git clone https://github.com/hamid-kordi/sample-backend-fastapi.git
```

Go to the project directory

```bash
  cd sample-backend-fastapi
```

Install docker on your os and run 

```bash
  docker-compose up --build
```

The server has started to work



## Comming Soon 

- Rate Limiting(optional)

  - Implement rate limiting to  prevent abuse of the API.

- Testing (optional)
    - Write unit tests using Pytest.


## Clean Code and Bonus

Ensure that your code follows best practices for clean code. This includes:
- Properly structured project with a clear separation of concerns.
- Descriptive variable and function names.
- Comprehensive comments and documentation.
- Consistent code formatting and style.
- Efficient and optimized code.
## Authors


- [@hamid-kordi](https://github.com/hamid-kordi)