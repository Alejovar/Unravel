"""Entrypoint del worker de RQ: procesa los jobs de análisis en segundo
plano, para que la API responda de inmediato con un `analysis_id` en
estado `queued` (VeriGraph.md sección 7)."""

import logging

from rq import Worker

from app.queue import QUEUE_NAME, get_redis_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    connection = get_redis_connection()
    worker = Worker([QUEUE_NAME], connection=connection)
    logger.info("Unravel worker escuchando en la cola '%s'", QUEUE_NAME)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
