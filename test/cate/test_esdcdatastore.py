from unittest import TestCase


try:
    from cate.core.ds import DATA_STORE_REGISTRY
except ImportError:
    DATA_STORE_REGISTRY = None


class EsdcDataStoreTest(TestCase):
    def test_cate_init_registers_data_store(self):
        if DATA_STORE_REGISTRY is None:
            print("EsdcDataStoreTest not executed, no Cate found.")
            return

        from esdl.cate.esdc import cate_init
        cate_init()

        data_store = DATA_STORE_REGISTRY.get_data_store('esdc')
        self.assertIsNotNone(data_store)
        self.assertEqual(data_store.id, 'esdc')
        self.assertEqual(data_store.title, 'Earth System Data Cube')


