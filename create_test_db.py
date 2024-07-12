import psycopg2
from config import load_config


def create_tables():
    """Create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE ProjectModel (
            project_pk SERIAL PRIMARY KEY,
            title VARCHAR(100) UNIQUE NOT NULL,
            description TEXT NOT NULL,
            logo VARCHAR(200),
            created_at TIMESTAMP NOT NULL,
            deleted_at TIMESTAMP,
            active BOOLEAN NOT NULL
        )
        """,
        """ CREATE TABLE TaskModel (
            task_pk SERIAL PRIMARY KEY,
            title VARCHAR(100) UNIQUE NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(255) NOT NULL, 
            executor_id INTEGER,
            executor_name VARCHAR(255),
            due_date TIMESTAMP,
            created_at TIMESTAMP NOT NULL,
            deleted_at TIMESTAMP,
            active BOOLEAN NOT NULL, 
            FOREIGN KEY (project) 
            REFERENCES ProjectModel (project_pk)
                ON DELETE CASCADE            
        )
        """,
        """
        CREATE TABLE TaskSubscribersModel (
                subscription_pk SERIAL PRIMARY KEY,
                FOREIGN KEY (task_id)
                REFERENCES TaskModel (task_pk)
                ON DELETE CASCADE,
                task_status VARCHAR(255) NOT NULL,
                subscriber_id INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE ProjectParticipantsModel (
                participation_pk SERIAL PRIMARY KEY,
                FOREIGN KEY (project_id)
                    REFERENCES ProjectModel (project_pk)
                    ON DELETE CASCADE,
                participant_id INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE TasksAttachmentsModel (
                attachment_pk SERIAL PRIMARY KEY,
                FOREIGN KEY (task_id)
                    REFERENCES TaskModel (task_pk)
                    ON DELETE CASCADE,
                attachment VARCHAR(200) NOT NULL
        )
        """,
    )
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


if __name__ == '__main__':
    create_tables()
