# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
from apiclient import errors
import httplib2
import unittest

from airflow import configuration, DAG
from airflow.contrib.operators.cloudml_operator import CloudMLBatchPredictionOperator

from mock import patch

DEFAULT_DATE = datetime.datetime(2017, 6, 6)

INPUT_MISSING_ORIGIN = {
    'dataFormat': 'TEXT',
    'inputPaths': ['gs://legal-bucket/fake-input-path/*'],
    'outputPath': 'gs://legal-bucket/fake-output-path',
    'region': 'us-east1',
}

SUCCESS_MESSAGE_MISSING_INPUT = {
    'jobId': 'test_prediction',
    'predictionOutput': {
        'outputPath': 'gs://fake-output-path',
        'predictionCount': 5000,
        'errorCount': 0,
        'nodeHours': 2.78
    },
    'state': 'SUCCEEDED'
}

DEFAULT_ARGS = {
    'project_id': 'test-project',
    'job_id': 'test_prediction',
    'region': 'us-east1',
    'data_format': 'TEXT',
    'input_paths': ['gs://legal-bucket-dash-Capital/legal-input-path/*'],
    'output_path': 'gs://12_legal_bucket_underscore_number/legal-output-path',
    'task_id': 'test-prediction'
}


class CloudMLBatchPredictionOperatorTest(unittest.TestCase):

    def setUp(self):
        super(CloudMLBatchPredictionOperatorTest, self).setUp()
        configuration.load_test_config()
        self.dag = DAG(
            'test_dag',
            default_args={
                'owner': 'airflow',
                'start_date': DEFAULT_DATE,
                'end_date': DEFAULT_DATE,
            },
            schedule_interval='@daily')

    def testSuccessWithModel(self):
        with patch('airflow.contrib.operators.cloudml_operator.CloudMLHook') \
                as mock_hook:

            input_with_model = INPUT_MISSING_ORIGIN.copy()
            input_with_model['modelName'] = \
                'projects/test-project/models/test_model'
            success_message = SUCCESS_MESSAGE_MISSING_INPUT.copy()
            success_message['predictionInput'] = input_with_model

            hook_instance = mock_hook.return_value
            hook_instance.get_job.side_effect = errors.HttpError(
                resp=httplib2.Response({
                    'status': 404
                }), content=b'some bytes')
            hook_instance.create_job.return_value = success_message

            prediction_task = CloudMLBatchPredictionOperator(
                job_id='test_prediction',
                project_id='test-project',
                region=input_with_model['region'],
                data_format=input_with_model['dataFormat'],
                input_paths=input_with_model['inputPaths'],
                output_path=input_with_model['outputPath'],
                model_name=input_with_model['modelName'].split('/')[-1],
                dag=self.dag,
                task_id='test-prediction')
            prediction_output = prediction_task.execute(None)

            mock_hook.assert_called_with('google_cloud_default', None)
            hook_instance.create_job.assert_called_with(
                'test-project',
                {
                    'jobId': 'test_prediction',
                    'predictionInput': input_with_model
                })
            self.assertEquals(
                success_message['predictionOutput'],
                prediction_output)

    def testSuccessWithVersion(self):
        with patch('airflow.contrib.operators.cloudml_operator.CloudMLHook') \
                as mock_hook:

            input_with_version = INPUT_MISSING_ORIGIN.copy()
            input_with_version['versionName'] = \
                'projects/test-project/models/test_model/versions/test_version'
            success_message = SUCCESS_MESSAGE_MISSING_INPUT.copy()
            success_message['predictionInput'] = input_with_version

            hook_instance = mock_hook.return_value
            hook_instance.get_job.side_effect = errors.HttpError(
                resp=httplib2.Response({
                    'status': 404
                }), content=b'some bytes')
            hook_instance.create_job.return_value = success_message

            prediction_task = CloudMLBatchPredictionOperator(
                job_id='test_prediction',
                project_id='test-project',
                region=input_with_version['region'],
                data_format=input_with_version['dataFormat'],
                input_paths=input_with_version['inputPaths'],
                output_path=input_with_version['outputPath'],
                model_name=input_with_version['versionName'].split('/')[-3],
                version_name=input_with_version['versionName'].split('/')[-1],
                dag=self.dag,
                task_id='test-prediction')
            prediction_output = prediction_task.execute(None)

            mock_hook.assert_called_with('google_cloud_default', None)
            hook_instance.create_job.assert_called_with(
                'test-project',
                {
                    'jobId': 'test_prediction',
                    'predictionInput': input_with_version
                })
            self.assertEquals(
                success_message['predictionOutput'],
                prediction_output)

    def testSuccessWithURI(self):
        with patch('airflow.contrib.operators.cloudml_operator.CloudMLHook') \
                as mock_hook:

            input_with_uri = INPUT_MISSING_ORIGIN.copy()
            input_with_uri['uri'] = 'gs://my_bucket/my_models/savedModel'
            success_message = SUCCESS_MESSAGE_MISSING_INPUT.copy()
            success_message['predictionInput'] = input_with_uri

            hook_instance = mock_hook.return_value
            hook_instance.get_job.side_effect = errors.HttpError(
                resp=httplib2.Response({
                    'status': 404
                }), content=b'some bytes')
            hook_instance.create_job.return_value = success_message

            prediction_task = CloudMLBatchPredictionOperator(
                job_id='test_prediction',
                project_id='test-project',
                region=input_with_uri['region'],
                data_format=input_with_uri['dataFormat'],
                input_paths=input_with_uri['inputPaths'],
                output_path=input_with_uri['outputPath'],
                uri=input_with_uri['uri'],
                dag=self.dag,
                task_id='test-prediction')
            prediction_output = prediction_task.execute(None)

            mock_hook.assert_called_with('google_cloud_default', None)
            hook_instance.create_job.assert_called_with(
                'test-project',
                {
                    'jobId': 'test_prediction',
                    'predictionInput': input_with_uri
                })
            self.assertEquals(
                success_message['predictionOutput'],
                prediction_output)

    def testInvalidModelOrigin(self):
        # Test that both uri and model is given
        task_args = DEFAULT_ARGS.copy()
        task_args['uri'] = 'gs://fake-uri/saved_model'
        task_args['model_name'] = 'fake_model'
        with self.assertRaises(ValueError) as context:
            CloudMLBatchPredictionOperator(**task_args).execute(None)
        self.assertEquals('Ambiguous model origin.', str(context.exception))

        # Test that both uri and model/version is given
        task_args = DEFAULT_ARGS.copy()
        task_args['uri'] = 'gs://fake-uri/saved_model'
        task_args['model_name'] = 'fake_model'
        task_args['version_name'] = 'fake_version'
        with self.assertRaises(ValueError) as context:
            CloudMLBatchPredictionOperator(**task_args).execute(None)
        self.assertEquals('Ambiguous model origin.', str(context.exception))

        # Test that a version is given without a model
        task_args = DEFAULT_ARGS.copy()
        task_args['version_name'] = 'bare_version'
        with self.assertRaises(ValueError) as context:
            CloudMLBatchPredictionOperator(**task_args).execute(None)
        self.assertEquals(
            'Missing model origin.',
            str(context.exception))

        # Test that none of uri, model, model/version is given
        task_args = DEFAULT_ARGS.copy()
        with self.assertRaises(ValueError) as context:
            CloudMLBatchPredictionOperator(**task_args).execute(None)
        self.assertEquals(
            'Missing model origin.',
            str(context.exception))

    def testHttpError(self):
        http_error_code = 403

        with patch('airflow.contrib.operators.cloudml_operator.CloudMLHook') \
                as mock_hook:
            input_with_model = INPUT_MISSING_ORIGIN.copy()
            input_with_model['modelName'] = \
                'projects/experimental/models/test_model'

            hook_instance = mock_hook.return_value
            hook_instance.create_job.side_effect = errors.HttpError(
                resp=httplib2.Response({
                    'status': http_error_code
                }), content=b'Forbidden')

            with self.assertRaises(errors.HttpError) as context:
                prediction_task = CloudMLBatchPredictionOperator(
                    job_id='test_prediction',
                    project_id='test-project',
                    region=input_with_model['region'],
                    data_format=input_with_model['dataFormat'],
                    input_paths=input_with_model['inputPaths'],
                    output_path=input_with_model['outputPath'],
                    model_name=input_with_model['modelName'].split('/')[-1],
                    dag=self.dag,
                    task_id='test-prediction')
                prediction_task.execute(None)

                mock_hook.assert_called_with('google_cloud_default', None)
                hook_instance.create_job.assert_called_with(
                    'test-project',
                    {
                        'jobId': 'test_prediction',
                        'predictionInput': input_with_model
                    })

            self.assertEquals(http_error_code, context.exception.resp.status)

    def testFailedJobError(self):
        with patch('airflow.contrib.operators.cloudml_operator.CloudMLHook') \
                as mock_hook:
            hook_instance = mock_hook.return_value
            hook_instance.create_job.return_value = {
                'state': 'FAILED',
                'errorMessage': 'A failure message'
            }
            task_args = DEFAULT_ARGS.copy()
            task_args['uri'] = 'a uri'

            with self.assertRaises(RuntimeError) as context:
                CloudMLBatchPredictionOperator(**task_args).execute(None)

            self.assertEquals('A failure message', str(context.exception))


if __name__ == '__main__':
    unittest.main()
