"""RQ worker entrypoint: processes analysis jobs in the background so the
API can answer immediately with an `analysis_id` in the `queued` state
(VeriGraph.md section 7)."""

import logging

from rq import Worker

from app.queue import QUEUE_NAME, get_redis_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    connection = get_redis_connection()
    worker = Worker([QUEUE_NAME], connection=connection)
    logger.info("Unravel worker listening on queue '%s'", QUEUE_NAME)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
