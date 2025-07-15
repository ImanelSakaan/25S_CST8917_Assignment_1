# CST8917 Assignment 1: Durable Workflow for Image Metadata Processing

---

## 📸 Demo Video

🎥 Watch the demo here:  
**[▶️ YouTube Video Link](https://youtu.be/ke40vtXDjCM)**

---
## 🛠️ Prerequisites

- ✅ Azure Subscription  
- ✅ Python 3.8+  
- ✅ [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)  
- ✅ [Azure Functions Core Tools v4](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)  
- ✅ [Visual Studio Code](https://code.visualstudio.com/) + Azure Functions extension  
- ✅ Azure Storage Account  
- ✅ Azure SQL Database  
- ✅ `ODBC Driver 17 for SQL Server` (for Ubuntu 24.04, see notes below)

---
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

### 🚀 Updated Implementation for Azure Functions v2

#### Step 1: Update `requirements.txt`

```txt
azure-functions>=1.18.0
azure-functions-durable>=1.2.9
Pillow==10.0.0
pyodbc
azure-storage-blob
````

---

#### Step 2: Create `function_app.py` (Main Application File)

Create a `function_app.py` file in your project root. This will contain all your function definitions using the v2 programming model.

---

#### Step 3: Update Project Structure

With the v2 model, you no longer need individual folders for each function. Your project structure should look like this:

```
image-metadata-processor/
├── function_app.py          # Main application file (all functions)
├── requirements.txt         # Dependencies
├── host.json                # Function app configuration
├── local.settings.json      # Local environment settings
├── .gitignore               # Git ignore file
└── README.md                # Documentation
```
---

### Step 4: Test Locally

To run your Azure Function App locally:

```bash
# Start the function app
func start
````
<img width="1253" height="679" alt="image" src="https://github.com/user-attachments/assets/a22e8eb0-b775-4674-bd5c-2441d703f21b" />


---
<img width="1270" height="659" alt="image" src="https://github.com/user-attachments/assets/40bcb74c-b5dd-4767-9fe3-6d04f9eca308" />


```


```







