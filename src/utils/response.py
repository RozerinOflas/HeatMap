from sdks.novavision.src.helper.package import PackageHelper
from components.HeatMap.src.models.PackageModel import PackageModel,PackageConfigs,ConfigExecutor,HeatMapExecutor,HeatMapExecutorOutputs,HeatMapExecutorResponse,OutputImage


def build_response(context):
    outputImage = OutputImage(value=context.image)
    heatMapExecutorOutputs = HeatMapExecutorOutputs(outputImage=outputImage)
    heatMapExecutorResponse = HeatMapExecutorResponse(outputs=heatMapExecutorOutputs)
    heatMapExecutor = HeatMapExecutor(value=heatMapExecutorResponse)
    executor = ConfigExecutor(value=heatMapExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel
