# CST8917 Assignment 1: Durable Workflow for Image Metadata Processing

---

## Objective

Build a **serverless image metadata processing pipeline** using **Azure Durable Functions** in **Python**. This assignment challenges you to use **blob triggers**, **activity functions**, and **output bindings**, and to **deploy** a complete solution to Azure. You'll simulate a real-world event-driven system.

---
## 📸 Demo Video

🎥 Watch the demo here:  
**[▶️ YouTube Video Link](https://youtu.be/ke40vtXDjCM)**
## Scenario

A fictional content moderation team wants to analyze the metadata of user-uploaded images. Your Durable Functions app should:

- Automatically **trigger** when a new image is uploaded to blob storage.
- **Extract metadata** (e.g., file size, format, dimensions).
- **Store the metadata** in an Azure SQL Database.

---

## Workflow 
---

### 🏗️ The 4 Function Types in Our Solution

---

#### 1. Client Function (Blob Trigger)

* **Triggers automatically** when a new image is uploaded to blob storage
* **Validates** the file format (only `.jpg`, `.png`, `.gif` allowed)
* **Starts** the orchestration workflow

---

#### 2. Orchestrator Function (The Coordinator)

* **Coordinates** the entire workflow
* **Calls activities** in the right order:

  1. First: Extract metadata (PIL + blob read)
  2. Second: Store metadata in database (inserts into SQL DB)

---

#### 3. Activity Function #1 (Extract Metadata)

* **Downloads** the image from blob storage
* **Extracts** information:

  * File name
  * File size (in KB)
  * Width and height (pixels)
  * Image format (JPEG, PNG, GIF)

---

#### 4. Activity Function #2 (Store Data)

* **Takes** the extracted metadata
* **Saves** it to Azure SQL Database
* **Logs** success or failure

---

### 🔄 Complete Workflow Flow

📁 Image Upload → 🔔 Blob Trigger → 👔 Orchestrator → 🔍 Extract Metadata → 💾 Store in DB

---







