import cv2
import mediapipe as mp
import math
import os

# Verifica se o modelo task Lite foi baixado antes de prosseguir
modelo_path = 'pose_landmarker_lite.task'
if not os.path.exists(modelo_path):
    print(f"AVISO: Arquivo do modelo corporai {modelo_path} não encontrado no raiz do projeto.")
    landmarker = None
else:
    # Inicializa o framework atualizado do MediaPipe (Task-based API)
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=modelo_path),
        running_mode=VisionRunningMode.IMAGE
    )
    landmarker = PoseLandmarker.create_from_options(options)

def calculate_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def extract_features(image_path):
    if landmarker is None:
        return None

    # Load media file native API
    try:
        mp_image = mp.Image.create_from_file(image_path)
    except Exception as e:
        print(f"Erro ao abrir imagem com MediaPipe: {e}")
        return None
        
    results = landmarker.detect(mp_image)
    
    if not results.pose_landmarks:
        print("Erro: Nenhum corpo detectado na imagem.")
        return None
        
    # Pega os marcadores da primeira pessoa detectada na imagem [0]
    landmarks = results.pose_landmarks[0]
    
    # Índices conforme documentação MediaPipe Tasks
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    hip_width = calculate_distance(left_hip, right_hip)

    if hip_width == 0:
        hip_width = 0.01
        
    shoulder_hip_ratio = shoulder_width / hip_width
    
    return {
        "shoulder_width": shoulder_width,
        "hip_width": hip_width,
        "shoulder_hip_ratio": shoulder_hip_ratio
    }
