class base_model:
    def fit(self, features, labels=None):
        raise NotImplementedError()

    def predict(self, features):
        raise NotImplementedError()