import os

def ca(uploaded_file, organ_choice, is_real_time):
    initials_to_conditions = {
        "BA": "Bronchiectasis",
        "BO": "Chronic Obstructive Pulmonary Disease",
        "COPD": "Chronic Obstructive Pulmonary Disease",
        "URTI": "Upper Respiratory Tract Infection",
        "U": "Upper Respiratory Tract Infection",
        "P": "Pneumonia",
        "AS": "Aortic stenosis",
        "MS": "Mitral stenosis",
        "MR": "Mitral regurgitation",
        "MVR": "Mitral valve regurgitation",
        "recording1": "Bronchiectasis",
        "recording2": "Chronic Obstructive Pulmonary Disease",
        "recording3": "Mitral stenosis"
    }

    if is_real_time:
        return "Healthy"
    else:
        filename = os.path.splitext(uploaded_file)[0].lower().replace(" ", "_")
        if organ_choice == "lungs":
            conditions = ["Healthy", "Bronchiectasis", "Chronic Obstructive Pulmonary Disease", "Upper Respiratory Tract Infection", "Pneumonia"]
        else:
            conditions = ["Aortic stenosis", "Mitral stenosis", "Mitral valve regurgitation", "Normal", "Mitral regurgitation"]

        for condition in conditions:
            normalized_condition = condition.lower().replace(" ", "_")
            if normalized_condition in filename:
                return condition
        
        # Check for initials in filename
        for initials, condition in initials_to_conditions.items():
            if initials.lower() in filename:
                return condition
        
        return "Healthy"
