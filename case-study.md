# Career Advisor Chatbot Case Study

## Overview

The Career Advisor Chatbot is a serverless web application designed to simulate intelligent career guidance conversations. It enables users to ask career-related questions and receive helpful responses, while storing each chat session in AWS DynamoDB for future reference. Built with simplicity and scalability in mind, the system uses keyword-based logic to simulate AI replies and is structured to allow easy future upgrades to an LLM-based response engine like Hugging Face.

---

## Features

* **Serverless Architecture** using AWS Lambda
* **Persistent Chat History** stored in DynamoDB
* **Session Management** via a separate session index table
* **Simple AI Simulation** using `elif` keyword branching
* **Frontend/Backend Separation** for scalability
* **CORS Support** for frontend-backend communication
* **DELETE Endpoint** to wipe or remove specific sessions
* **Production-ready JSON API responses**

---

## Tech Stack

* **AWS Lambda** – Stateless serverless compute
* **AWS DynamoDB** – NoSQL storage for messages and sessions
* **API Gateway** – HTTP interface to Lambda
* **HTML/CSS/JavaScript** – Simple frontend interface
* **Python (Boto3)** – Backend logic for Lambda function

---

## Backend Structure

```
backend/
├── lambda_function.py     # Main Lambda handler
```

The Lambda function handles routing based on HTTP method and path. It supports:

* `GET /careerchat?sessionId=X` – Fetch messages for a session
* `GET /careerchat/sessions` – List all sessions
* `POST /careerchat` – Add user message, auto-generate AI response
* `DELETE /careerchat/sessions` – Delete all sessions
* `DELETE /careerchat?sessionId=X` – Delete a specific session

---

## Frontend Structure

```
frontend/
├── index.html             # UI to interact with the chatbot
```

A minimal HTML page allows users to:

* Type and send messages
* View session-based conversation history
* Start new sessions or delete old ones

---

## DynamoDB Design

* **Table 1: CareerAdvisorChats**

  * `sessionId` (Partition Key)
  * `timestamp` (Sort Key)
  * `type` ("user" or "ai")
  * `content` (message content)

* **Table 2: CareerAdvisorSessionIndex**

  * `sessionId` (Primary Key)
  * `title` (First user message or placeholder)
  * `createdAt` (timestamp)

---

## How It Works

1. **User types a message** into the web interface
2. **Frontend sends POST** request to Lambda via API Gateway
3. **Lambda matches keywords** like "developer" or "designer"
4. **Stores messages** in DynamoDB (user + AI response)
5. **Updates session index** if new session
6. **Replies with JSON** containing the AI's response

---

## What Makes It Interesting

* The chatbot mimics AI logic using readable `elif` statements, perfect for MVPs or demos
* Easy future integration with Hugging Face or OpenAI models (plug-and-play architecture)
* Fully serverless and low-cost, ideal for student or portfolio projects
* Great example of full-stack development using modern cloud-native tools

---
## Author Notes

This project was designed as a learning and showcase piece — demonstrating not only how to use AWS services like Lambda and DynamoDB, but also how to structure a scalable, serverless chatbot application. It's a foundation you can build on, whether you're preparing for interviews, enhancing your GitHub portfolio, or prototyping something bigger.

---

## Live Demo & GitHub

* **GitHub:** [github.com/JustinKlair/Career-Advisor-Chatbot](https://github.com/JustinKlair/Career-Advisor-Chatbot)
