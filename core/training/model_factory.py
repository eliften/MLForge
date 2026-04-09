from train import RegressionTrainer, ClassificationTrainer, ClusteringTrainer

class ModelFactory:
    def create_trainer(self, task_type: str, model_name: str, params: dict):
        params = params or {}
        task_type = task_type.strip().lower()
        model_name = model_name.strip().lower()

        if task_type == "regression":
            return RegressionTrainer(model_name=model_name, params=params)
        elif task_type == "classification":
            return ClassificationTrainer(model_name=model_name, params=params)
        elif task_type == "clustering":
            return ClusteringTrainer(model_name=model_name, params=params)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
