CREATE TABLE ImageMetadata (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    FileName NVARCHAR(255) NOT NULL,
    FileSizeKB INT,
    Format NVARCHAR(50),
    Width INT,
    Height INT,
    UploadedAt DATETIME DEFAULT GETDATE()
);
