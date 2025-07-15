import azure.functions as func
import azure.durable_functions as df
import logging
import os
import io
import pyodbc
from PIL import Image
from azure.storage.blob import BlobServiceClient
from datetime import datetime

# Initialize the Function App
app = func.FunctionApp()

# -------------------------------
# 1- Blob Trigger → Starts Orchestration
# -------------------------------
# Triggers automatically when a new image is uploaded to blob storage

@app.blob_trigger(arg_name="myblob", 
                 path="images-input/{name}",
                 connection="AzureWebJobsStorage")
@app.durable_client_input(client_name="client")
async def blob_trigger_start_orchestration(myblob: func.InputStream, client: df.DurableOrchestrationClient) -> None:
    """
    Blob trigger function that starts the orchestration when a new image is uploaded.
    Triggers on .jpg, .png, .gif files only.
    """
    try:
        # Check if the blob is an image file (Validates the file format (only .jpg, .png, .gif allowed))
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        blob_name = myblob.name
        
        if not any(blob_name.lower().endswith(ext) for ext in allowed_extensions):
            logging.info(f"Skipping non-image file: {blob_name}")
            return
        
        # Prepare blob info for orchestration 
        blob_info = {
            "name": blob_name,
            "size": myblob.length,
            "uri": myblob.uri
        }
        
        # Start orchestration
        instance_id = await client.start_new("image_processing_orchestrator", None, blob_info)
        
        logging.info(f"Started orchestration with ID: {instance_id} for image: {blob_name}")
        
    except Exception as e:
        logging.error(f"Error in blob trigger: {str(e)}")
        raise
    
# -------------------------------
# 2- Orchestrator Function
# -------------------------------

@app.orchestration_trigger(context_name="context")
def image_processing_orchestrator(context: df.DurableOrchestrationContext):
    """
    Orchestrator function that coordinates the image processing workflow.
    """
    blob_info = context.get_input()
    
    logging.info(f"Orchestrator processing image: {blob_info['name']}")
    
    try:
        # Step 1: Extract metadata from the image
        metadata = yield context.call_activity("extract_metadata_activity", blob_info)
        
        # Step 2: Store metadata in Azure SQL Database
        storage_result = yield context.call_activity("store_metadata_activity", metadata)
        
        logging.info(f"Completed processing for: {blob_info['name']}")
        
        return {
            "status": "completed",
            "image": blob_info['name'],
            "metadata": metadata,
            "storage_result": storage_result
        }
        
    except Exception as e:
        # logging.error(f"Error in orchestrator: {str(e)}")
        logging.error(f"Error in orchestrator: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "image": blob_info['name'],
            "error": str(e)
        }
        
# -------------------------------
# 3- Activity: Extract Image Metadata
# -------------------------------

@app.activity_trigger(input_name="blob_info")
def extract_metadata_activity(blob_info: dict) -> dict:
    """
    Activity function to extract metadata from an image using PIL.
    """
    try:
        logging.info(f"Extracting metadata for: {blob_info['name']}")
        
        # Get blob service client
        connection_string = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Parse blob name to get container and blob name
        blob_parts = blob_info["name"].split("/")
        container_name = "images-input"
        blob_name = blob_parts[-1] if len(blob_parts) > 1 else blob_info["name"]
        
        # Download blob data
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_data = blob_client.download_blob().readall()
        
        # Extract metadata using PIL
        image = Image.open(io.BytesIO(blob_data))
        
        # Get file format from PIL
        image_format = image.format if image.format else "Unknown"
        
        metadata = {
            "file_name": blob_name,
            "file_size_kb": round(len(blob_data) / 1024, 2),
            "width": image.width,
            "height": image.height,
            "format": image_format
        }
        
        logging.info(f"Successfully extracted metadata: {metadata}")
        
        return metadata
        
    except Exception as e:
        logging.error(f"Error extracting metadata: {str(e)}")
        raise Exception(f"Failed to extract metadata: {str(e)}")
    
# -------------------------------
# 4- Activity: Store Metadata in Azure SQL
# -------------------------------

@app.activity_trigger(input_name="metadata")
def store_metadata_activity(metadata: dict) -> dict:
    """
    Activity function to store metadata in Azure SQL Database.
    """
    try:
        logging.info(f"Storing metadata for: {metadata['file_name']}")
        logging.info(f"Metadata values: {metadata}")
         
        # Get connection string from environment
        sql_connection_string = os.environ["SqlConnectionString"]
        
        # Connect to database
        with pyodbc.connect(sql_connection_string) as conn:
            cursor = conn.cursor()
            
            # Debug: Which DB are we connected to?
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            logging.info(f"Connected to database: {db_name}")


            # Insert metadata into database
            insert_query = """
            INSERT INTO ImageMetadata (FileName, FileSizeKB, Width, Height, Format, ProcessedDate)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            print("Insert executed")
            
            cursor.execute(insert_query, (
                metadata["file_name"],
                metadata["file_size_kb"],
                metadata["width"],
                metadata["height"],
                metadata["format"],
                datetime.now()
            ))
            
            logging.info(f"Rows affected: {cursor.rowcount}")
            conn.commit()
            logging.info("Insert committed.")

            
        result = {
            "status": "success",
            "message": f"Metadata stored successfully for {metadata['file_name']}",
            "timestamp": datetime.now().isoformat()
        }
        
        logging.info(f"Successfully stored metadata: {result}")
        
        return result
        
    except Exception as e:
        logging.error(f"Error storing metadata: {str(e)}")
        raise Exception(f"Failed to store metadata: {str(e)}")
    
# -------------------------------
# Manual Test Activity for SQL Insert
# -------------------------------
@app.activity_trigger(input_name="input")
def manual_insert_test(input: dict) -> str:
    try:
        logging.info("Running manual DB insert test...")

        sql = os.environ["SqlConnectionString"]
        with pyodbc.connect(sql) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ImageMetadata (FileName, FileSizeKB, Width, Height, Format, ProcessedDate)
                VALUES ('ManualTest.jpg', 123.45, 800, 600, 'JPEG', GETDATE())
            """)
            conn.commit()
            logging.info("Manual insert successful.")
        return "Manual insert success"

    except Exception as e:
        logging.error(f"Manual insert failed: {str(e)}", exc_info=True)
        return "Manual insert failed"


# -------------------------------
# Health Check Endpoint
# -------------------------------

# Optional: Add a health check endpoint
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple health check endpoint to verify the function app is running.
    """
    return func.HttpResponse(
        "Image Processing Function App is healthy!",
        status_code=200
    )

# Optional: Add a manual trigger endpoint for testing
@app.route(route="manual-trigger", auth_level=func.AuthLevel.FUNCTION)
@app.durable_client_input(client_name="client")
async def manual_trigger(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:
    """
    Manual trigger endpoint for testing the orchestration with a specific image.
    """
    try:
        # Get image name from query parameters
        image_name = req.params.get('image_name')
        
        if not image_name:
            return func.HttpResponse(
                "Please provide 'image_name' parameter",
                status_code=400
            )
        
        # Create mock blob info for testing
        blob_info = {
            "name": image_name,
            "size": 0,  # Will be determined during processing
            "uri": f"https://stgimageprocessor123.blob.core.windows.net/images-input/{image_name}"
        }
        
        # Start orchestration
        instance_id = await client.start_new("image_processing_orchestrator", None, blob_info)
        
        return func.HttpResponse(
            f"Started manual orchestration with ID: {instance_id}",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in manual trigger: {str(e)}")
        return func.HttpResponse(
            f"Error starting orchestration: {str(e)}",
            status_code=500
        )