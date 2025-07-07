from drf_yasg.utils import swagger_auto_schema

import torch
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models_ai.air_quality.air_quality_lstm_model import AirQualityLSTM
from api.models_ai.air_quality.air_quality_scaler import scaler
from api.utils.aq_utils import get_aq_matrix_10h

model = AirQualityLSTM(input_size=9, output_size=5, lstm_size=128, n_lstm_layers=2, dense_layers=[32, 16], dropout_rate=0.0)
model.load_state_dict(torch.load("api/models_ai/air_quality/air_quality_epoch-750.pt", map_location=torch.device('cpu')))
model.eval()

class AirQualityPredictView(APIView):

    @swagger_auto_schema(
        tags=['Predict'],
    )
    def get(self, request):
        try:

            data = get_aq_matrix_10h()
            data = np.expand_dims(data, axis=0)
            original_shape = data.shape

            data_2d = data.reshape(-1, original_shape[2])
            data_scaled = scaler.transform(data_2d)
            data_scaled_3d = data_scaled.reshape(original_shape)

            input_tensor = torch.tensor(data_scaled_3d, dtype=torch.float32)

            with torch.no_grad():
                output = model(input_tensor)

            logits = output.numpy()[0]
            exp_scores = np.exp(logits - np.max(logits))
            probas = exp_scores / np.sum(exp_scores)
            probas = [round(p, 5) for p in probas.tolist()]

            return Response({
                "aq_probabilities": probas
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)