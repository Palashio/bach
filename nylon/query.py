from nylon.supplementaries.main import dataset_initializer
from nylon.supplementaries.handlers import (preprocess_module, modeling_module, analysis_module)
import uuid
import pandas as pd

class Polymer:
    '''
    Constructor for the Polymer class.
    :param dataset_path is the path to the dataset
    :param save_model: whether the model should be saved in a .sav file
    '''

    def __init__(self, dataset_path, save_model=False, custom_files=[]):
        self.df = dataset_path
        self.json_file = None
        self.y = None
        self.model = None
        self.results = None
        self.custom_files = custom_files
        self.history = {}
        self.dataframe = None
        self.latest_id = None

        self.pcaDebug = False
        self.runPCA = False
        if(self.runPCA):
            self.pca_df = None
            self.pca_df_trans = None
            self.pca_model = None
            self.column_names = None

    def run(self, json_file_path, as_dict=False):
        '''
        Runs the dataset on a json file specification
        :param json_file_path path to json file for
        '''

        if self.model is not None:
            self.update_history(json_file_path)

        request_info = {'df': self.df, 'json': json_file_path, 'y': None, 'model': 'None', 'analysis': None,
                        'custom': self.custom_files, 'pca': self.runPCA}

        pipeline = [
            dataset_initializer,
            preprocess_module,
            modeling_module,
            analysis_module
        ]
        
        if(self.pcaDebug):
            pipeline = [dataset_initializer, preprocess_module]

        for a_step in pipeline:
            request_info = a_step(request_info)

        self.set_class_after_run(request_info)

        return self

    def update_history(self, json_file_path):
        self.history[self.latest_id] = {'df': self.df, 'json': json_file_path, 'y': self.y,
                                        'model': self.model, 'results': self.results}


    def set_class_after_run(self, request_info):
        new_id = str(uuid.uuid4())
        self.latest_id = new_id

        self.results = request_info['analysis']
        self.model = request_info['model']
        self.json_file = request_info['json']
        self.y = request_info['y']

        if(self.runPCA and 'pca_model' in request_info):
            self.pca_model = request_info['pca_model']
            self.column_names = request_info['original_names']
            self.pca_df = request_info['pca_df']
            self.pca_df_trans = dict()
            self.pca_df_trans['train'] = self.transformToPrinciple(self.pca_df['train'])
            self.pca_df_trans['test'] = self.transformToPrinciple(self.pca_df['test'])
    
    def transformToPrinciple(self, values):
        if not self.runPCA:
            return None
        transformed = self.pca_model.transform(values)
        num_columns = transformed.shape[1]
        column_names = ["Principal#" + str(i + 1) for i in range(num_columns)]
        transform_df = pd.DataFrame(transformed, columns = column_names)
        return transform_df
    
    def transformToInput(self, transformed): 
        if not self.runPCA:
            return None
        original = self.pca_model.inverse_transform(transformed)
        num_columns = original.shape[1]
        assert num_columns == len(self.column_names)
        original_df = pd.DataFrame(original, columns = self.column_names)
        return original_df