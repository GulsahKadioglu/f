# Threat Model for the Federated Cancer Screening Platform

## Introduction

This document outlines potential security threats to the platform and the measures in place to mitigate them. The goal is to ensure the confidentiality, integrity, and availability of the system and its data.

## System Components

The primary components considered in this model are:

- **Backend API:** The central server providing RESTful services.
- **Frontend:** The Next.js web application used by doctors and administrators.
- **Database:** The PostgreSQL database storing metadata and application data.
- **FL Clients (Nodes):** Local institution servers participating in federated learning.
- **FL Server:** The central server orchestrating the training process.

## Potential Threats and Mitigations

| Threat ID | Threat Description | Component(s) Affected | Severity | Mitigation Strategy |
|---|---|---|---|---|
| **T01** | **Eavesdropping on Network Traffic (Man-in-the-Middle)** | All services | **High** | Enforce **TLS/HTTPS** for all communication between clients, the backend API, and federated learning services. Use a reverse proxy like Nginx to manage TLS termination. |
| **T02** | **Unauthorized Access to Data at Rest** | Database, Secure Storage | **High** | Utilize **full-disk encryption** on servers. Enforce strong, rotated credentials for database access. Implement strict file system permissions to limit access to storage directories. |
| **T03** | **Inference of Private Data from Model Updates** | FL Server, FL Clients | **High** | **Homomorphic Encryption (HE):** Model updates are encrypted before leaving the client node. The server performs aggregation on the encrypted data without decryption. <br><br> **Differential Privacy:** (Optional but recommended) Add statistical noise to model updates to prevent reverse-engineering of individual data points from the aggregated model. |
| **T04** | **Malicious FL Client (Model Poisoning)** | FL Server | **Medium** | Authenticate and authorize all participating FL clients. Implement anomaly detection and validation checks on incoming model updates to identify and reject malicious or malformed contributions. |
| **T05** | **Cross-Site Scripting (XSS)** | Frontend | **Medium** | Utilize the built-in security features of the Next.js framework. Ensure all user-generated content is properly sanitized before being rendered in the UI. |
| **T06** | **Broken Access Control** | Backend API, Frontend | **High** | Implement and enforce Role-Based Access Control (RBAC) on the backend. Ensure that API endpoints verify user roles and permissions before executing an operation. The frontend should dynamically render UI components based on user permissions. |
| **T07** | **Insecure Direct Object References (IDOR)** | Backend API | **High** | When accessing resources (e.g., a medical case or report), verify not only that the user is authenticated but also that they are authorized to access that specific resource (e.g., they are the assigned doctor or an administrator). |

## Disclaimer

This is a high-level threat model intended to guide development and deployment. A comprehensive security audit should be performed before deploying the platform in a live, production environment handling real patient data.
