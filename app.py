import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Loading DynamoAuth backend...")
    from app.main import app
    logger.info("✓ FastAPI app loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load app: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")