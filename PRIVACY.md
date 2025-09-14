# Privacy Policy for the Federated Cancer Screening Platform

**Last Updated:** September 9, 2025

## Our Commitment to Privacy

This project is fundamentally designed around the principle of privacy-preserving machine learning. We understand the sensitivity of medical data, and our architecture is built to ensure that raw patient data is never exposed or shared.

## Core Privacy-Preserving Architecture

Our platform does **not** collect or store personal health information on a central server for the purpose of model training. Instead, we use state-of-the-art privacy-enhancing technologies.

### 1. Federated Learning (FL)

The core of our platform is a federated learning system, powered by the Flower framework. The process works as follows:

- **Data Stays Local:** Raw data (such as mammogram images and patient reports) **never leaves** the local premises of the participating institution (e.g., the hospital's own server).
- **Local Training:** The machine learning model is trained directly on the local data within the institution's secure environment.
- **Model Updates, Not Data:** Only the abstract mathematical model updates (weights or gradients) are sent to the central server for aggregation. Raw data is never transmitted.

### 2. Homomorphic Encryption (HE)

To provide an even stronger layer of security, all model updates are encrypted before they leave the institution's server.

- **Encryption Before Transmission:** We use the TenSEAL library to apply homomorphic encryption to the model updates.
- **Secure Aggregation:** The central server aggregates these encrypted updates *without ever decrypting them*. This means the central server cannot reverse-engineer the updates to infer anything about the underlying data.

### Visual Data Flow

To make the process clearer, here is a simplified visual representation of the data flow in a single federated learning round:

```
+---------------------------------+         +---------------------------------+
|        Hospital A (Node)        |         |        Hospital B (Node)        |
|                                 |         |                                 |
|  [Raw Patient Data] <---------- | -------> |  [Raw Patient Data] <---------- |
|  (Never Leaves the Server)      |         |  (Never Leaves the Server)      |
|                                 |         |                                 |
|  1. Local Model Training        |         |  1. Local Model Training        |
|     |                           |         |     |                           |
|     v                           |         |     v                           |
|  [Model Update]                 |         |  [Model Update]                 |
|                                 |         |                                 |
|  2. Encrypt Update (HE)         |         |  2. Encrypt Update (HE)         |
|     |                           |         |     |                           |
|     v                           |         |     v                           |
|  [Encrypted Update]             |         |  [Encrypted Update]             |
+---------------------------------+         +---------------------------------+
             |                                     |
             |  3. Send Encrypted Updates to Server  |
             +-------------------------------------+
                                   |
                                   v
                  +---------------------------------+
                  |      Federated Learning Server  |
                  |                                 |
                  |  4. Secure Aggregation          |
                  |     (On Encrypted Data)         |
                  |                                 |
                  |  [Aggregated Encrypted Update]  |
                  |                                 |
                  |  5. Update Global Model         |
                  |                                 |
                  |  [New Global Model] -------------> (Sent back to nodes
                  +---------------------------------+    for next round)
```

### 3. Data in Transit

All communication between the client applications (web, mobile, FL nodes) and the backend server must be secured using **TLS/HTTPS** to prevent eavesdropping.

### 4. Data at Rest

While no raw training data is stored centrally, any application-related data (such as user accounts or aggregated, anonymized metrics) is stored in a PostgreSQL database. We recommend and assume a production environment where the database and any file storage are encrypted at rest.

## Disclaimer

This document is a technical summary of the privacy-preserving features of the platform architecture. It is not a legally binding privacy policy. The deployment and management of this platform in a real-world environment must be done in compliance with all local data protection regulations such as HIPAA, GDPR, or KVKK.
