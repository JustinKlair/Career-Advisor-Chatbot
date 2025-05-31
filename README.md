# 🧠 Career Advisor Chatbot (AWS-Powered)

A lightweight AI-like chatbot built using AWS Lambda, API Gateway, and DynamoDB — with no paid AI model. Instead, it simulates intelligence through custom `elif` branching logic based on user input.

## 🔍 Overview

This chatbot helps users get career advice based on what they type — simulating an AI conversation by analyzing keyword intent through `elif` branches. Inspired by the ChatGPT interface, it includes:

- Chat history
- "New Chat" functionality
- Chat deletion
- Fast serverless backend
- Free-tier AWS setup (no model costs!)

---

## 🏗️ Architecture

- **Frontend:** HTML + JavaScript 
- **Backend:** AWS Lambda (Python)
- **API Gateway:** Handles HTTP requests
- **Database:** DynamoDB (stores chat history)
- **Deployment:** AWS Console

---

## ⚙️ How It Works

1. **User types a question** → frontend sends request to Lambda.
2. **Lambda function** parses input and uses `elif` statements to simulate a response.
3. **Responses** are stored in **DynamoDB** along with session IDs.
4. UI displays history like ChatGPT's sidebar.

---

## 💡 Example Interactions

> **User:** "What careers are good for people who like coding?"  
> **Bot:** "Careers in software development, data science, or cybersecurity could be a good fit for you."

> **User:** "Clear my chat history"  
> **Bot:** "Your chat history has been cleared."

## 🧑‍💻 Built By
Justin ([@JustinKlair](https://github.com/JustinKlair)
