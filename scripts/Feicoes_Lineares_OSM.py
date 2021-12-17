"""
Model exported as python.
Name : Feições Lineares OSM
Group : Identificação de Feições Homólogas
With QGIS : 31614
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class FeiesLinearesOsm(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('ref', 'Adicione a camada de referência:', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterString('geg (2)', 'Defina um valor (value) OSM:', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterString('geg (2) (2)', 'Defina uma chave (key) OSM:', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('CruzamentosHomlogos', 'Cruzamentos Homólogos', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(22, model_feedback)
        results = {}
        outputs = {}

        # Baixar dados OSM
        alg_params = {
            'EXTENT': parameters['ref'],
            'KEY': parameters['geg (2) (2)'],
            'SERVER': 'https://lz4.overpass-api.de/api/interpreter',
            'TIMEOUT': 25,
            'VALUE': parameters['geg (2)']
        }
        outputs['BaixarDadosOsm'] = processing.run('quickosm:downloadosmdataextentquery', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extrair pontos de cruzamentos (1)
        alg_params = {
            'INPUT': parameters['ref'],
            'INPUT_FIELDS': [''],
            'INTERSECT': parameters['ref'],
            'INTERSECT_FIELDS': ['0'],
            'INTERSECT_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPontosDeCruzamentos1'] = processing.run('native:lineintersections', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Coordenada E (Ref)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'E_Ref',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '$x',
            'INPUT': outputs['ExtrairPontosDeCruzamentos1']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CoordenadaERef'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Coordenada N (Ref)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'N_Ref',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '$y',
            'INPUT': outputs['CoordenadaERef']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CoordenadaNRef'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Buffer (Ref)
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 6,
            'END_CAP_STYLE': 0,
            'INPUT': outputs['CoordenadaNRef']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferRef'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Mesclar camadas OSM
        alg_params = {
            'CRS': outputs['BufferRef']['OUTPUT'],
            'LAYERS': [outputs['BaixarDadosOsm']['OUTPUT_LINES'],outputs['BaixarDadosOsm']['OUTPUT_MULTILINESTRINGS']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MesclarCamadasOsm'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extrair pontos de cruzamentos (2)
        alg_params = {
            'INPUT': outputs['MesclarCamadasOsm']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'INTERSECT': outputs['MesclarCamadasOsm']['OUTPUT'],
            'INTERSECT_FIELDS': ['0'],
            'INTERSECT_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtrairPontosDeCruzamentos2'] = processing.run('native:lineintersections', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Coordenada E (OSM)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'E_OSM',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '$x',
            'INPUT': outputs['ExtrairPontosDeCruzamentos2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CoordenadaEOsm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Coordenada N (OSM)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'N_OSM',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '$y',
            'INPUT': outputs['CoordenadaEOsm']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CoordenadaNOsm'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Interseção 
        alg_params = {
            'INPUT': outputs['CoordenadaNOsm']['OUTPUT'],
            'INPUT_FIELDS': ['E_OSM','N_OSM'],
            'OVERLAY': outputs['BufferRef']['OUTPUT'],
            'OVERLAY_FIELDS': ['E_Ref','N_Ref'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Interseo'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Excluir geometrias duplicadas
        alg_params = {
            'INPUT': outputs['Interseo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExcluirGeometriasDuplicadas'] = processing.run('native:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Distância Euclidiana
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Dist. Euclidiana',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'sqrt((( \"E_OSM\" - \"E_Ref\" )^\'2\')+(( \"N_OSM\" - \"N_Ref\")^\'2\'))',
            'INPUT': outputs['ExcluirGeometriasDuplicadas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistnciaEuclidiana'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Gerar ID
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'ID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': ' $id ',
            'INPUT': outputs['DistnciaEuclidiana']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GerarId'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # RMS
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'RMS',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))',
            'INPUT': outputs['GerarId']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rms'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # 1:1000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:1000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=0.28) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.17\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=0.50) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.30\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=0.80) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.50\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=1.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.60\nTHEN \'Classe D\' ELSE \'Rejeitado\'\nEND',
            'INPUT': outputs['Rms']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # 1:2000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:2000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=0.56) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.34\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=1.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.60\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=1.6) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=1.0\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=2.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=1.2\nTHEN \'Classe D\' ELSE \'Rejeitado\' END\n',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # 1:5000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:5000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=1.4) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=0.85\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=2.5) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=1.5\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=4.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=2.5\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=5.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=3\nTHEN \'Classe D\'\nELSE \'Rejeitado\' END',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # 1:10000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:10000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=2.8) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=1.7\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=5.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=3.0\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=8.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=5.0\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=10.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=6.0\nTHEN \'Classe D\'\nELSE \'Rejeitado\' END',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # 1:25000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:25000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=7.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=4.25\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=12.50) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=7.5\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=20.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=12.5\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=25.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=15.0\nTHEN \'Classe D\' ELSE \'Rejeitado\'\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # 1:50000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:50000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=14.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=8.51\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=25.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=15.0\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=40.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=25.0\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=50.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=30.0\nTHEN \'Classe D\'\nELSE \'Rejeitado\' END',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # 1:100000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:100000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': '\nCASE WHEN sum(\"Dist. Euclidiana\"<=28.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=17.02\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=50.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=30.0\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=80.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=50.0\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=100.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=60.0\nTHEN \'Classe D\' ELSE \'Rejeitado\'\nEND',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # 1:250000
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': '1:250000',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': 'CASE WHEN sum(\"Dist. Euclidiana\"<=70.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=42.55\nTHEN \'Classe A\'\nWHEN sum(\"Dist. Euclidiana\"<=125.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=75.0\nTHEN \'Classe B\'\nWHEN sum(\"Dist. Euclidiana\"<=200.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=125.0\nTHEN \'Classe C\'\nWHEN sum(\"Dist. Euclidiana\"<=250.0) >= 0.9*count(\"ID\") AND sqrt(sum(\"Dist. Euclidiana\"^2)/count(\"ID\"))<=150.0\nTHEN \'Classe D\' ELSE \'Rejeitado\'\nEND\n',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': parameters['CruzamentosHomlogos']
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CruzamentosHomlogos'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return 'Feições Lineares OSM'

    def displayName(self):
        return 'Feições Lineares OSM'

    def group(self):
        return 'Identificação de Feições Homólogas'

    def groupId(self):
        return 'Identificação de Feições Homólogas'

    def shortHelpString(self):
        return """<html><body><h2>Descrição do Algoritmo</h2>
<p>Este algoritimo identifica o cruzamento em feições lineares e realiza a comparação de uma base de referência a uma base definida por uma chave (key) e um valor (value) do Open Street Map (OSM). Esta comparação resulta numa camada pontual apresentando os pontos de cruzamento da camada avaliada considerados homólogos à camada de referência.

Além disso, a ferramenta permite a avaliação da acurácia posicional das feições considerando as escalas do Mapeamento Sistemático Brasileiro e o Padrão de Exatidão Cartográfica para Produtos Cartográficos Digitais (PEC PCD).

O algoritimo também realiza o download de todos os tipos de feições (ponto, linha, polígono) encontradas no OSM para o valor definido da via.</p>
<h2>Parâmetros de entrada</h2>
<h3>Adicione a camada de referência:</h3>
<p>Selecionar o shapefile considerado como base de referência.</p>
<h3>Defina um valor (value) OSM:</h3>
<p>Definir o tipo ou categoria da chave OSM.</p>
<h3>Defina uma chave (key) OSM:</h3>
<p>Definir a chave OSM.</p>
<h3>Cruzamentos Homólogos</h3>
<p>Camada vetorial dos pontos de cruzamento do OSM considerados homólogos aos cruzamentos de referência.</p>
<h2>Saídas</h2>
<h3>Cruzamentos Homólogos</h3>
<p>Camada vetorial dos pontos de cruzamento do OSM considerados homólogos aos cruzamentos de referência.</p>
<br><p align="right">Autor do algoritmo: Guilherme Neivas</p><p align="right">Versão do Algoritmo: 1.0</p></body></html>"""

    def createInstance(self):
        return FeiesLinearesOsm()
