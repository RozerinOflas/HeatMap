
from sdks.novavision.src.helper.package import PackageHelper
from components.HeatMap.src.models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor, GeneralExecutor ,GeneralExecutorOutputs, GeneralExecutorResponse, IdExecutor ,IdExecutorOutputs, IdExecutorResponse, PackageExecutor, OutputImage


def build_responseGeneral(context):
    outputImage = OutputImage(value=context.image)
    generalExecutorOutputs = GeneralExecutorOutputs(outputImage=outputImage)
    generalExecutorResponse = GeneralExecutorResponse(outputs=generalExecutorOutputs)
    generalExecutorExecutor = GeneralExecutor(value=GeneralExecutorResponse)
    executor = ConfigExecutor(value=generalExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel

def build_responseId(context):
    outputImage = OutputImage(value=context.image)
    idExecutorOutputs = IdExecutorOutputs(outputImage=outputImage)
    idExecutorResponse = IdExecutorResponse(outputs=idExecutorOutputs)
    idExecutorExecutor = IdExecutor(value=idExecutorResponse)
    executor = ConfigExecutor(value=idExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel