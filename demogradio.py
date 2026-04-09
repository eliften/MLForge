import gradio as gr
import pandas as pd, os, requests

def update_models(project_type):
    if project_type == "Regression":
        return gr.update(choices=["LinearRegression", "Ridge", "Lasso", "ElasticNet", "SVR", "Decision Tree", "Random Forest", "XGBoost", "LightGBM"], value="LinearRegression", interactive=True)

    if project_type == "Classification":
        return gr.update(choices=["LogisticRegression", "Decision Tree", "RandomForest", "XGBoost", "SVM", "KNN", "Naive Bayes"], value="LogisticRegression", interactive=True)

    if project_type == "Clustering":
        return gr.update(choices=["KMeans", "DBSCAN", "GaussianMixture", "AgglomerativeClustering"], value="KMeans", interactive=True)

    return gr.update(choices=["Önce proje seç"], value="Önce proje seç", interactive=False)


def display_csv(file, project_type, model_name):
    if not file:
        return gr.update(), gr.update(), "Dosya yüklenmedi"

    file_path = file.name
    name = os.path.basename(file_path)

    try:
        if file_path.endswith((".xlsx", ".xls")):
            data = pd.read_excel(file_path, engine="openpyxl")
        else:
            try:
                data = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                data = pd.read_csv(file_path, encoding="latin1")

    except Exception as e:
        return gr.update(), gr.update(), f"Hata: {str(e)}"

    cols = list(data.columns)

    return (
        gr.update(
            choices=cols,
            value=cols[:-1],
            interactive=True,
            show_select_all=True,
            label="FEATURES"
        ),
        gr.update(
            choices=cols,
            value=cols[-1],
            interactive=True,
            label="TARGET"
        ),
        f"Proje: {project_type}\nModel: {model_name}\nDosya: {name}\n\nPreview:\n{data.head()}"
    )
def send_to_api(p_name: str, type: str, models: str, dataset: str, test_size: float, random_state: int, target: str, features: list):
    url = "http://localhost:8000/data"
    payload = {
        "name": p_name,
        "type": type,
        "models": models,
        "dataset": dataset,
        "test_size": test_size,
        "random_state": random_state,
        "target": target,
        "features": features
    }
    response = requests.post(url, json=payload)
    return str(response.json())

with gr.Blocks() as demo:
    gr.Markdown("## MLForge - Machine Learning Project Management Tool\n\nDEMO")

    with gr.Row():
        with gr.Column(scale=1):
            project_name = gr.Textbox(placeholder="Project Name", label="Project Name", interactive=True)
            gr.Markdown("### Girdiler")

            file_input = gr.File(label="Dosya Yükle")

            project_dropdown = gr.Dropdown(
                choices=["Choices", "Regression", "Classification", "Clustering"],
                label="Proje Seç"
            )

            model_dropdown = gr.Dropdown(
                choices=["Firstlyselect a model type"],
                label="Model Seç",
                interactive=False
            )

            test_size_slider = gr.Slider(0.1, 0.5, value=0.2, step=0.05, label="Test Set Oranı", interactive=True)
            random_state = gr.Slider(0, 100, value=42, step=1, label="Random State", interactive=True)
            submit_btn = gr.Button("Submit", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Outputs")
            output = gr.Markdown()
            features_output = gr.CheckboxGroup()
            target_output = gr.Radio()

            run_btn = gr.Button("Run", variant="primary")
            

    project_dropdown.change(
        fn=update_models,
        inputs=project_dropdown,
        outputs=model_dropdown
    )

    submit_btn.click(
        fn=display_csv,
        inputs=[file_input, project_dropdown, model_dropdown],
        outputs=[features_output, target_output, output]
    )

    run_btn.click(
        fn=send_to_api,
        inputs=[
            project_name,
            project_dropdown,
            model_dropdown,
            file_input,
            test_size_slider,
            random_state,
            target_output,
            features_output
        ],
        outputs=output
    )

demo.launch(debug=True)