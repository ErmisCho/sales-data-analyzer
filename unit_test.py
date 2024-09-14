import unittest
import pandas as pd
from sales_data_analyzer import ConfigurationManager, DataLoader, DataAnalyzer


class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        input_file = "input_sales.csv"
        results_path = "results"
        self.conf = {
            "input_file": input_file,
            "results_path": results_path,
            "product_column_name": "produkt",
            "customer_column_name": "kunde",
            "seller_column_name": "verkäufer",
            "status_column_name": "status",
            "status_accepted": "verkauft",
            "status_rejected": "abgelehnt",
            "seller_effectiveness_column": "Total Effectiveness (%)",
            "unoferred_products_filename": "Unoffered Products.png",
            "seller_coverage_column": "Total Coverage (%)",
            "seller_effectiveness_filename": "Seller Effectiveness.png",
            "seller_coverage_filename": "Seller Coverage.png"
        }
        self.configuration_manager = ConfigurationManager()
        self.data_loader = DataLoader(input_file)
        self.data_analyzer = DataAnalyzer(
            self.conf, input_file, results_path)

    def tearDown(self) -> None:
        del self.conf
        del self.configuration_manager
        del self.data_loader
        del self.data_analyzer

    def test_configuration_manager_read_configuration(self) -> None:
        """Tests if read_configuration function of ConfigurationManager returns a non-empty dictionary."""
        conf: dict = self.configuration_manager.read_configuration()
        self.assertIsInstance(conf, dict)
        self.assertTrue(conf)

    def test_data_loader_read_data(self) -> None:
        """Tests if read_data function of DataLoader returns a non-empty pandas DataFrame."""
        data: pd.DataFrame = self.data_loader.read_data(self.conf)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)

    def test_data_analyzer_calculate_unoffered_products(self) -> None:
        """Tests if calculate_unoffered_products function of DataAnalyzer generates a non-empty pandas DataFrame for unoffered products."""
        self.data_analyzer.calculate_unoffered_products()
        unoffered_products: pd.DataFrame = self.data_analyzer.unoffered_products
        self.assertIsInstance(unoffered_products, pd.DataFrame)
        self.assertFalse(unoffered_products.empty)

    def test_data_analyzer_calculate_seller_effectiveness(self) -> None:
        """Tests if calculate_seller_effectiveness function of DataAnalyzer generates a non-empty pandas DataFrame for seller effectiveness."""
        self.data_analyzer.calculate_seller_effectiveness(self.conf)
        seller_effectiveness: pd.DataFrame = self.data_analyzer.seller_effectiveness
        self.assertIsInstance(seller_effectiveness, pd.DataFrame)
        self.assertFalse(seller_effectiveness.empty)

    def test_data_analyzer_calculate_seller_coverage(self) -> None:
        """Tests if calculate_seller_coverage function of DataAnalyzer generates a non-empty pandas DataFrame for seller coverage."""
        self.data_analyzer.calculate_seller_coverage(self.conf)
        seller_coverage: pd.DataFrame = self.data_analyzer.seller_offer_coverage
        self.assertIsInstance(seller_coverage, pd.DataFrame)
        self.assertFalse(seller_coverage.empty)


if __name__ == '__main__':
    unittest.main()
