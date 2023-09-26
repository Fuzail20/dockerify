import ast
import textwrap
import os
import subprocess

mapping = {
        "PIL": "pillow"
    }

def replace_wrong_import_statements(arr):
    for i in range(len(arr)):
        if arr[i] in mapping:
            arr[i] = mapping[arr[i]]

def extract_imports(code):
    import_statements = []

    dedented_code = textwrap.dedent(code)

    try:
        tree = ast.parse(dedented_code)
    except SyntaxError as e:
        print(f"Error: Invalid Python code - {e}")
        return []

    for node in ast.walk(tree):
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                print("alias: " + alias.name)
                package_name = alias.name.split(".")[0]
                import_statements.append(package_name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module.split(".")[0]
            print("module: "+module_name)
            import_statements.append(module_name)
            # for alias in node.names:
            #     print("modukle alias: "+alias.name)
            #     package_name = f"{module_name}.{alias.name.split('.')[0]}"
            #     import_statements.append(package_name)

    print("import statements with wrong keys: ")
    print(import_statements)

    replace_wrong_import_statements(import_statements)

    print("import statements with correct keys: ")
    print(import_statements)

    return import_statements

def create_dockerfile(code, dependencies):
    dockerfile_content = f"""
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
    """

    requirements_content = '\n'.join(dependencies)

    with open("Dockerfile", "w") as dockerfile:
        dockerfile.write(dockerfile_content)

    with open("requirements.txt", "w") as requirements:
        requirements.write(requirements_content)

    with open("app.py", "w") as app_file:
        app_file.write(code)

def build_and_push_docker_image(image_name, dockerhub_username):
    try:
        subprocess.run(["docker", "build", "-t", image_name, "."], check=True)
        subprocess.run(["docker", "tag", image_name, f"{dockerhub_username}/{image_name}"], check=True)
        subprocess.run(["docker", "push", f"{dockerhub_username}/{image_name}"], check=True)
        print("Docker image successfully built and pushed to Docker Hub.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while building or pushing Docker image: {e}")

if __name__ == "__main__":
    # Get the Python code as input
    # python_code = input("Enter Python code: ")
    with open('input.txt', 'r') as file:
        python_code = file.read()
    

    # Extract dependencies from the input Python code
    dependencies = extract_imports(python_code)
    
    print(dependencies)

    # Create the Dockerfile and requirements.txt based on extracted dependencies
    create_dockerfile(python_code, dependencies)

    # Build and push the Docker image to Docker Hub
    image_name = "my_python_app_6"
    dockerhub_username = "fuzail21"  # Replace with your Docker Hub username
    build_and_push_docker_image(image_name, dockerhub_username)

    # Clean up temporary files
    os.remove("Dockerfile")
    os.remove("requirements.txt")
    os.remove("app.py")
