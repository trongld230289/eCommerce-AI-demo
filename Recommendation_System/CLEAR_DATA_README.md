# Recommendation System Data Cleanup

This directory contains data cleanup utilities for the Recommendation System vector database and cache.

## Files

### `clear_all_data.py`
Main cleanup script for the Recommendation System that clears:
- **Chroma DB Collections**: `user_events`, `product_embeddings`, and other vector collections
- **Vector Database Files**: Complete removal of Chroma DB files and directories
- **Cache Files**: Python cache files and temporary data

### `test_clear_data.py`
Test script to demonstrate the cleanup functionality with test data.

## Usage

### Basic Cleanup
```bash
cd Recommendation_System
python clear_all_data.py
```

### Before Running
1. **Stop the Recommendation Service** first for complete file cleanup:
   ```bash
   # Stop the Flask recommendation server (Ctrl+C in terminal)
   ```

2. **Confirm the action** when prompted:
   ```
   Do you want to continue? (type 'yes' to confirm): yes
   ```

## What Gets Cleared

### ✅ Always Cleared
- **Collection Data**: All items in Chroma DB collections are removed
- **Cache Files**: Python `__pycache__`, `.pytest_cache`, etc.

### ⚠️ May Require Service Stop
- **Vector Database Files**: Complete removal of `./chroma_db/` directory
- **Database Storage**: SQLite files and vector storage files

## Output Example

```
Recommendation System Data Cleanup Script
=============================================
This will clear:
• All Chroma DB collections (user_events, product_embeddings)
• Vector database files
• Cache files and directories

⚠️  WARNING: This action cannot be undone!
💡 TIP: Stop the recommendation service first for complete cleanup

🗄️  Clearing Chroma DB collections...
📋 Found 2 collections: ['user_events', 'product_embeddings']
🧹 Clearing collection: user_events
✅ Cleared 13 items from 'user_events'

📁 Clearing vector database files...
✅ Cleared vector database files completely

💾 Clearing cache files...
✅ Cleared 1 cache directories

✅ Recommendation System cleanup completed successfully!
```

## Integration

This script is designed to work alongside the Backend's `clear_all_data.py`:

- **Backend Script**: Clears Firebase Firestore and cache
- **Recommendation Script**: Clears Chroma DB vectors and cache
- **Separation of Concerns**: Each service manages its own data

## Safety Features

- **Confirmation Required**: Must type 'yes' to proceed
- **Service Detection**: Warns if vector files are locked by running services
- **Verification**: Reports cleanup results and remaining data
- **Error Handling**: Graceful handling of missing collections or locked files

## Troubleshooting

### File Access Errors
```
❌ Could not clear vector database files: [WinError 32] The process cannot access the file
💡 TIP: Stop the recommendation service first, then try again
```
**Solution**: Stop the Flask recommendation server and run the script again.

### Collection Not Found
```
Collection 'collection_name' does not exist, skipping...
```
**Normal**: This is expected if collections haven't been created yet.

### Chroma DB Not Available
```
⚠️  Chroma DB not available
```
**Solution**: Install ChromaDB: `pip install chromadb`
