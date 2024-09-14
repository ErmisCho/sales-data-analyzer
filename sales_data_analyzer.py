import os
import configparser
import logging
import tkinter as tk
import dataframe_image as dfi
import pandas as pd
from pathlib import Path
from tkinter import filedialog
from datetime import datetime
import warnings


class ConfigurationManager:
    """This class is responsible for reading a configuration file
    """

    def __init__(self, conf_file="conf.ini"):
        """Initiates the constructor for readinf a configuration file

        Args:
            conf_file (str, optional): Filename of the configuration file. Defaults to "conf.ini".
        """
        self.conf_file = conf_file

    def read_configuration(self) -> dict:
        """Reads the configuration file

        Returns:
            conf (dict): Includes user coonfiguration options
        """

        conf = {}
        if os.path.exists(self.conf_file):
            config = configparser.ConfigParser()
            config.read(self.conf_file, encoding='utf-8')

            # Read and update paths
            if 'Paths' in config:
                if 'results_path' in config['Paths']:
                    conf["results_path"] = config['Paths']['results_path']
                if 'input_file' in config['Paths']:
                    conf["input_file"] = config['Paths']['input_file']

            # Read and update column names
            if 'Column Names' in config:

                # input file related settings
                if 'product_column_name' in config['Column Names']:
                    conf["product_column_name"] = config['Column Names']['product_column_name']
                if 'customer_column_name' in config['Column Names']:
                    conf["customer_column_name"] = config['Column Names']['customer_column_name']
                if 'seller_column_name' in config['Column Names']:
                    conf["seller_column_name"] = config['Column Names']['seller_column_name']
                if 'status_column_name' in config['Column Names']:
                    conf["status_column_name"] = config['Column Names']['status_column_name']

                # output file related settings
                if 'seller_effectiveness_column' in config['Column Names']:
                    conf["seller_effectiveness_column"] = config[
                        'Column Names']['seller_effectiveness_column']+" (%)"
                if 'seller_coverage_column' in config['Column Names']:
                    conf["seller_coverage_column"] = config['Column Names']['seller_coverage_column'] + \
                        " (%)"

            # Read and update acceptable statuses
            if 'Status' in config:
                if 'status_accepted' in config['Status']:
                    conf["status_accepted"] = config['Status']['status_accepted']
                if 'status_rejected' in config['Status']:
                    conf["status_rejected"] = config['Status']['status_rejected']

            # Read and update filenames in the output folder related settings
            if 'Output Filenames' in config:
                if 'unoferred_products_filename' in config['Output Filenames']:
                    conf["seller_effectiveness_filename"] = config[
                        'Output Filenames']['unoferred_products_filename']
                if 'seller_effectiveness_filename' in config['Output Filenames']:
                    conf["seller_effectiveness_filename"] = config[
                        'Output Filenames']['seller_effectiveness_filename']
                if 'seller_coverage_filename' in config['Output Filenames']:
                    conf["seller_coverage_filename"] = config['Output Filenames']['seller_coverage_filename']

        else:
            logging.warning(
                "Configuration file not found. Using default values.")
        return conf


class DataLoader:
    """Responsible for reading an input .csv file
    """

    def __init__(self, input_file):
        """Constructor for reading a .csv file

        Args:
            input_file (str): Filename of the input .csv file
        """
        self.input_file = input_file

    def read_data(self, conf):
        """Reads a configuration file and saves the user options to a dictionary

        Args:
            conf (dict): contains user options

        Raises:
            ValueError: functions fails if the ..csv file is not appropriately formated due to ommited columns)

        Returns:
            DataFrame: contains the input file
        """

        try:
            # Read data from the input file
            if not os.path.isfile(self.input_file):
                root = tk.Tk()
                root.withdraw()

                conf["input_file"] = filedialog.askopenfilename()
                if conf["input_file"] == "":
                    logging.error(
                        "No file was selected. Restart the tool and select a file.")
                    os._exit(1)

            self.data = pd.read_csv(self.input_file)

            required_columns = [
                conf["customer_column_name"],
                conf["seller_column_name"],
                conf["product_column_name"],
                conf["status_column_name"]
            ]

            missing_columns = [
                col for col in required_columns if col not in self.data.columns]

            if missing_columns:
                raise ValueError(
                    f"{conf['input_file']}: Missing required columns: {', '.join(missing_columns)}")

        except Exception as e:
            # Handle any exceptions raised during data reading or column checking
            logging.error(f"An error occurred while reading data: {e}")
            self.data = None  # Set data to None to indicate failure
            os._exit(1)

        conf["customers"] = list(
            self.data[conf["customer_column_name"]].unique())
        conf["customers"].sort(reverse=False)
        return self.data


class DataAnalyzer:
    def __init__(self, conf, input_file="input_sales.csv", results_path="results"):
        """Responsible for analyzing csv files of sellers and customers

        Args:
            conf (dict): contains user configuration options set through a configuration file
            input_file (str): Filename of the input file. Defaults to "input_sales.csv".
            results_path (str): Path where the results are going to be saved at. Defaults to "results".
        """

        default_values = {
            "input_file": input_file,
            "results_path": results_path,
            "product_column_name": "produkt",
            "customer_column_name": "kunde",
            "seller_column_name": "verkäufer",
            "status_column_name": "status",
            "status_accepted": "verkauft",
            "status_rejected": "abgelehnt",
            "seller_effectiveness_column": "Total Effectiveness (%)",
            "unoferred_products_filename": "Unoffered_Products.png",
            "seller_coverage_column": "Total Coverage (%)",
            "seller_effectiveness_filename": "Seller Effectiveness.png",
            "seller_coverage_filename": "Seller Coverage.png"
        }
        for key, value in default_values.items():
            setattr(self, key, conf.get(key, value))

        self.unoffered_products = pd.DataFrame()
        self.seller_effectiveness = pd.DataFrame()
        self.seller_offer_coverage = pd.DataFrame()

        data_loader = DataLoader(self.input_file)
        self.data = data_loader.read_data(conf)

    def calculate_unoffered_products(self):
        """Calculates the products which have not been offered to customers yet and saves the results in a 2D pandas Dataframe
        """

        all_products = set(self.data[self.product_column_name].unique())
        self.unoffered_products = pd.DataFrame(
            columns=[self.product_column_name, self.customer_column_name])
        for customer_name, per_customer_data in self.data.groupby(self.customer_column_name):
            items_to_be_recommended = list(all_products -
                                           set(per_customer_data[self.product_column_name].tolist()))

            the_dict = {self.customer_column_name: [customer_name]*len(items_to_be_recommended),
                        self.product_column_name: items_to_be_recommended}

            df_the_dict = pd.DataFrame(
                the_dict, columns=[self.customer_column_name, self.product_column_name])

            self.unoffered_products = pd.concat(
                [self.unoffered_products, df_the_dict], ignore_index=True)

            self.data = pd.concat([self.data, df_the_dict], ignore_index=True)
        self.unoffered_products = self.unoffered_products.sort_values(
            by=[self.product_column_name, self.customer_column_name])

        self.unoffered_products = self.unoffered_products.pivot_table(
            index=self.customer_column_name, columns=self.product_column_name, aggfunc=any, fill_value="")
        self.unoffered_products = self.unoffered_products.replace(True,  "X")

    def calculate_seller_effectiveness(self, conf):
        """Calculates every seller's overall and on a per customer basis effectiveness and saves the results in a 2D pandas Dataframe

        Args:
            conf (dict): contains the user configuration options
        """

        column_names = [self.seller_column_name] + \
            conf["customers"]+[self.seller_effectiveness_column]
        self.seller_effectiveness = pd.DataFrame(columns=column_names)

        for seller_name, per_seller_data in self.data.groupby(self.seller_column_name):
            # calculating the total effectiveness of a seller

            successfull_sales = per_seller_data[per_seller_data[self.status_column_name]
                                                == self.status_accepted].shape[0]
            total_sales = per_seller_data[self.status_column_name].notna(
            ).sum()
            effectiveness = (successfull_sales/total_sales) * \
                100 if total_sales else 0

            # calculating the effectiveness of a seller per customer
            per_customer_effectiveness_dict = {}
            for customer_name, per_customer_data in per_seller_data.groupby(self.customer_column_name):

                per_customer_successfull_sales = per_customer_data[per_customer_data[self.status_column_name]
                                                                   == self.status_accepted].shape[0]
                per_customer_total_sales = per_customer_data[self.status_column_name].notna(
                ).sum()
                per_customer_effectiveness = (
                    per_customer_successfull_sales/per_customer_total_sales) * 100 if per_customer_total_sales else 0.0

                per_customer_effectiveness_dict[customer_name] = per_customer_effectiveness

            per_seller_per_customer_data = []
            for customer in conf["customers"]:
                per_seller_per_customer_data.append(
                    per_customer_effectiveness_dict.get(customer, 0))

            self.seller_effectiveness.loc[len(self.seller_effectiveness)] = [
                seller_name] + per_seller_per_customer_data + [effectiveness]

        self.seller_effectiveness = self.seller_effectiveness.sort_values(
            by=[self.seller_effectiveness_column, self.seller_column_name], ascending=False)

        self.round_up_numbers(self.seller_effectiveness)

    def calculate_seller_coverage(self, conf):
        """Calculates every seller's overall and on a per customer basis coverage and saves the results in a 2D pandas Dataframe

        Args:
            conf (dict): contains the user configuration options
        """

        column_names = [self.seller_column_name] + \
            conf["customers"]+[self.seller_coverage_column]
        self.seller_offer_coverage = pd.DataFrame(columns=column_names)
        total_offers = self.data[self.status_column_name].notna().sum()

        for seller_name, per_seller_data in self.data.groupby(self.seller_column_name):
            # calculate the offer coverage of a seller

            seller_offers = per_seller_data[self.status_column_name].notna(
            ).sum()
            seller_total_coverage = (
                seller_offers/total_offers)*100 if total_offers else 0

            # calculate the offer coverage of a seller per customer
            per_customer_coverage_dict = {}
            for customer_name, per_customer_data in self.data.groupby(self.customer_column_name):
                per_customer_offers = per_customer_data[self.status_column_name].notna(
                ).sum()
                seller_offers = per_customer_data[per_customer_data[self.seller_column_name] == seller_name].notna(
                ).shape[0]
                per_customer_coverage = (
                    seller_offers/per_customer_offers) * 100 if per_customer_offers else 0.0
                per_customer_coverage_dict[customer_name] = per_customer_coverage

            per_seller_per_customer_data = []
            for customer in conf["customers"]:
                per_seller_per_customer_data.append(
                    per_customer_coverage_dict.get(customer, 0))

            self.seller_offer_coverage.loc[len(self.seller_offer_coverage)] = [
                seller_name] + per_seller_per_customer_data + [seller_total_coverage]

        self.seller_offer_coverage = self.seller_offer_coverage.sort_values(
            by=[self.seller_coverage_column, self.seller_column_name], ascending=False)

        self.round_up_numbers(self.seller_offer_coverage)

    def round_up_numbers(self, df):
        """Rounds up the numbers and converts all cells to of a string type in a dataframe

        Args:
            df (pd.DataFrame): any pandas Dataframe
        """
        for column in df.columns:
            try:
                df[column] = df[column].astype(
                    'float64')
                df[column] = df[column].apply(
                    lambda x: str(round(x)))

            except ValueError:
                pass
        df.replace("0", "", inplace=True)

    def create_results_folder(self):
        """Creates the path where the result of the execution is going to be saved
        """
        try:
            current_timestamp = datetime.now().strftime(
                'Analysis_Results_%Y-%m-%d_%H-%M-%S')
            self.results_path = os.path.join(
                self.results_path, current_timestamp)
            Path(self.results_path).mkdir(parents=True, exist_ok=True)
        except PermissionError:
            logging.error(
                f"Permission Denied: Failed to create a folder in the specified output path{self.results_path}")
            os._exit(1)

    def save_results(self, df="all"):
        """Saves the supplied dataframe(s) into pictures for user visibility
           By default it exports as picture all of the dataframes. If a dataframe is supplied, then only this dataframe is exported as a picture

        Args:
            df (str | pd.DataFrame): If it's a DataFrame then it contains information potentially about sellers, customers and products. Defaults to "all".
        """

        self.create_results_folder()
        # fix: to prevent warning coming up because of using later dfi.export with the switch table_conversion="matplotlib" on
        warnings.filterwarnings("ignore", category=FutureWarning)

        if (f'{self.unoffered_products=}'.split('=')[0]) == "self.unoffered_products" or (type(df) == str and df == "all"):
            self.unoffered_products.style.background_gradient(cmap='Blues')
            dfi.export(self.unoffered_products, os.path.join(
                self.results_path, self.unoferred_products_filename), table_conversion="matplotlib")

        if (f'{self.seller_effectiveness=}'.split('=')[0]) == "self.seller_effectiveness" or (type(df) == str and df == "all"):
            self.seller_effectiveness
            self.seller_effectiveness.style.background_gradient(
                cmap='Blues')
            self.seller_effectiveness.style.hide(axis='index')
            dfi.export(self.seller_effectiveness.style.hide(), os.path.join(
                self.results_path, self.seller_effectiveness_filename), table_conversion="matplotlib")

        if (f'{self.seller_offer_coverage=}'.split('=')[0]) == "self.seller_offer_coverage" or (type(df) == str and df == "all"):
            self.seller_offer_coverage
            self.seller_offer_coverage.style.background_gradient(
                cmap='Blues')
            self.seller_offer_coverage.style.hide(axis='index')
            dfi.export(self.seller_offer_coverage.style.hide(), os.path.join(
                self.results_path, self.seller_coverage_filename), table_conversion="matplotlib")
        logging.info(f"Output generated under: {self.results_path}")


if __name__ == '__main__':

    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.INFO)
    logging.info("Initiated ...")

    config_manager = ConfigurationManager()
    conf = config_manager.read_configuration()

    data_analyzer = DataAnalyzer(conf)

    data_analyzer.calculate_unoffered_products()
    data_analyzer.calculate_seller_effectiveness(conf)
    data_analyzer.calculate_seller_coverage(conf)
    data_analyzer.save_results()

    logging.info("Completed successfully.")
