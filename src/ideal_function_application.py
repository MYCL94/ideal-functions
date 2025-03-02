from pathlib import Path
import logging.config
import uvicorn

if __name__ == "__main__":
    # logger configuration
    logger_config = logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel('INFO')

    logger.info('Service: \'%s\' started', Path(__file__).stem)

    uvicorn.run(
        'src.application.rest.ideal_functions_API:app',
        host='0.0.0.0',
        port=8080,
        log_config=logger_config,
    )

    logger.info('Service: \'%s\' shutdown', Path(__file__).stem)
