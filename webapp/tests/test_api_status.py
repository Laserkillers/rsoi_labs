import json
import os
import unittest
from io import StringIO

import psycopg2
import testing.postgresql
from pathlib import Path
from dotenv import load_dotenv

base_path = '/api/v1/'

def modify_env(params: dict):
    config = StringIO(
        f"DB_NAME={params['database']}\n"
        f"DB_USER={params['user']}\n"
        f"DB_PORT={params['port']}\n"
        f"DB_PASSWORD=\n"
        f"DB_HOST={params['host']}\n"
        f"DEBUG_MODE=1"
        )
    load_dotenv(stream=config)


class StatusAppTests(unittest.TestCase):
    status_mapping = base_path + 'check_status'
    person_mapping = base_path + 'persons'

    @classmethod
    def setUpClass(cls) -> None:
        pass
        # Generate Postgresql class which shares the generated database
        # cls.Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)
        # cls.postgresql = cls.Postgresql()
        # modify_env(cls.postgresql.dsn())
        #
        # with psycopg2.connect(**cls.postgresql.dsn()) as conn:
        #     with conn.cursor() as cursor:
        #
        #         if Path(os.getcwd()).name != 'tests':
        #             path_to_queries = Path(os.getcwd()) / 'migrations'
        #         else:
        #             path_to_queries = Path(os.getcwd()).parent.parent / 'migrations'
        #
        #         for filename in os.listdir(path_to_queries):
        #             with open(path_to_queries / filename) as file:
        #                 if filename.startswith('fill'):
        #                     continue
        #                 query = ''.join(file.readlines())
        #                 cursor.execute(query)
        #     conn.commit()

    def setUp(self) -> None:
        # path = Path(os.getcwd()).parent
        from src import ProgramConfiguration, routes, ServerConfiguration
        self.app = ServerConfiguration('gunicorn').app
        # self.app.config['TESTING'] = True
        self.app.register_blueprint(routes)
        self.app = self.app.test_client()

        self.app_config = ProgramConfiguration()

    def test_run_status(self):
        res = self.app.get(self.status_mapping)
        self.assertEqual(200, res.status_code, f'This mapping is not working: "{self.status_mapping}"')

    def test_check_add_entity(self):
        test_entity = {
            'name': 'test',
            'age': 0,
            'address': 'test_adress',
            'work': 'test_work'
        }
        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)
        for entity in all_entities:
            self.app.delete(self.person_mapping + f"/{entity['id']}")
        initial_len = 0

        res = self.app.post(self.person_mapping, data=test_entity)

        self.assertEqual(
            201,
            res.status_code,
            f'Add entity is not working: "{self.status_mapping}". '
            f'Status code: {res.status_code}.'
            f'Request body: {res.data}')

        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)

        self.assertEqual(1 + initial_len, len(all_entities), f'Count entities not same')
        all_entities[0].pop('id')
        self.assertEqual(test_entity, all_entities[0], 'Entities not same')

    def test_check_delete_entity(self):
        test_entity = {
            'name': 'test',
            'age': 0,
            'address': 'test_adress',
            'work': 'test_work'
        }
        self.app.post(self.person_mapping, data=test_entity)

        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)
        entity_id = all_entities[0].pop('id')
        prev_len = len(all_entities)
        res = self.app.delete(self.person_mapping + f"/{entity_id}")

        self.assertEqual(204, res.status_code, f'Status code is incorrect')

        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)
        self.assertEqual(prev_len - 1, len(all_entities), f"Entity dont deleted")

    def test_check_update_entity(self):
        test_entity = {
            'name': 'test',
            'age': 0,
            'address': 'test_adress',
            'work': 'test_work'
        }
        self.app.post(self.person_mapping, data=test_entity)
        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)
        entity_id = all_entities[0].pop('id')

        changed_entity = test_entity.copy()
        changed_entity['age'] = 20
        res = self.app.patch(self.person_mapping + f"/{entity_id}", data=changed_entity)
        self.assertEqual(200, res.status_code)

        res = self.app.get(self.person_mapping + f"/{entity_id}")
        all_entities = json.loads(res.data)
        all_entities.pop('id')
        self.assertEqual(changed_entity, all_entities, 'Entity doesnt changed')

    def test_get_all_entities(self):
        test_entity = {
            'name': 'test',
            'age': 0,
            'address': 'test_adress',
            'work': 'test_work'
        }
        time_repeat = 5
        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)
        initial_len = len(all_entities)
        for i in range(time_repeat):
            res = self.app.post(self.person_mapping, data=test_entity)
            self.assertEqual(201, res.status_code)

        res = self.app.get(self.person_mapping)
        all_entities = json.loads(res.data)
        self.assertEqual(time_repeat + initial_len, len(all_entities), 'Some entities is missing')


    @classmethod
    def tearDownClass(cls) -> None:
        pass
        # cls.postgresql.stop()
        # cls.Postgresql.clear_cache()


if __name__ == '__main__':
    unittest.main()
