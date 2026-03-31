def generate_recommendations(objetivo, imc, percentual_gordura_estimado, features_cv):
    """
    Etapa 6: Regras de Inteligência do Sistema
    Transforma dados matemáticos em orientações de treino práticas, conforme diferencial TCC.
    """
    treino = f"### Protocolo de Treino Adaptativo (BioVision AI)\n**Foco Estratégico:** {objetivo}\n\n"
    
    # Regra 1: Baseada no modelo de ML (Gordura)
    if percentual_gordura_estimado > 25:
         treino += "🔥 **Análise de IA**: Em nossas estimativas de composição, detectamos índices que exigem otimização metabólica.\n"
         treino += "- **Foco**: Alta queima calórica e condicionamento.\n"
         treino += "- **Ação Biovision**: Foram adicionados 40 minutos de cardio (HIIT/Corrida leve) para potencializar o gasto energético.\n\n"
    else:
         treino += "💪 **Análise de IA**: Composição corporal propícia para hipertrofia sistêmica e densidade muscular limpa.\n"
         treino += "- **Foco**: Progressão de cargas e sobrecarga progressiva.\n\n"
    
    # Regra 2: Baseada na Visão Computacional (MediaPipe / Relação Cintura/Ombro)
    shoulder_hip_ratio = features_cv.get("shoulder_hip_ratio", 1.0) if features_cv else 1.0
    
    # Se o quadril for mais largo que os ombros (ou proporção baixa -> corpo tipo "pera")
    if shoulder_hip_ratio < 1.1:
         treino += "⚠️ **Análise Estrutural (Visão Computacional)**: Identificamos que a relação Ombro/Quadril está baixa (Ombros mais estreitos comparativamente).\n"
         treino += "- **Ação Biovision**: Para gerar assimetria saudável e estética em V, a IA prescreveu exercícios extra para a musculatura do deltoide e o grande dorsal.\n\n"
         
         treino += "## Treino A - Foco Superiores (Correção de Assimetria Visual)\n"
         treino += "- Desenvolvimento com Halteres: 4 séries x 10 repetições\n"
         treino += "- Elevação Lateral (Foco Total no Deltoide Médio): 5 séries x 12 a 15 repetições\n"
         treino += "- Puxada Frente (Foco Dorsal): 4 séries x 10 repetições\n"
         treino += "- Remada Curvada: 4 séries x 10 repetições\n"
         treino += "- Supino Reto Máquina: 3 séries x 12 repetições\n"
    else:
         treino += "✅ **Análise Estrutural (Visão Computacional)**: Proporção Ombro/Quadril excelente (Biotipo Atlético predominante).\n"
         
         treino += "## Treino A - Corpo Completo (Ganho de Força e Manutenção)\n"
         treino += "- Agachamento Livre: 4 séries x 8 a 10 repetições\n"
         treino += "- Supino Reto: 4 séries x 8 a 10 repetições\n"
         treino += "- Levantamento Terra: 4 séries x 6 a 8 repetições\n"
         treino += "- Leg Press 45: 3 séries pesadas\n"
         
    treino += "\n---\n*Nota Científica: Este treino não é aleatório. Foi gerado cruzando seus dados biométricos de base com análises espaciais da sua foto (*Pose Estimation*) aplicadas por nossos algoritmos RandomForest.*"
    return treino
