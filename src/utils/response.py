from sdks.novavision.src.helper.package import PackageHelper
from components.HeatMap.src.models.PackageModel import (
    PackageModel,
    PackageConfigs,
    HeatMapExecutor,
    HeatMapExecutorOutputs,
    HeatMapExecutorResponse,
    OutputImage,
)


def build_response(context):
    """
    Tek executor (HeatMapExecutor) için response oluşturur.
    """
    # Çıkış görüntüsünü hazırla
    outputImage = OutputImage(value=context.image)

    # Executor output
    executorOutputs = HeatMapExecutorOutputs(outputImage=outputImage)

    # Executor response
    executorResponse = HeatMapExecutorResponse(outputs=executorOutputs)

    # Executor instance
    executor = HeatMapExecutor(value=executorResponse)

    # Package configs
    packageConfigs = PackageConfigs(executor=executor)

    # Package oluştur
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)

    return packageModel
