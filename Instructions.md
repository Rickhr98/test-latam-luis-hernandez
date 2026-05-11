## Implementación del Challenge

Esta solución incluye:

- API desarrollada en `FastAPI`
- Base de datos MySQL (`users.db`)
- CRUD completo para `User`
- Validación con `Pydantic` y roles enumerados
- Documentación automática OpenAPI/Swagger en `/docs`
- Pruebas con `pytest`
- Dockerfile para contenerizar la aplicación
- `cloudbuild.yaml` para despliegue en Google Cloud Run

### Ejecutar localmente

1. Crear un entorno virtual y activar:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar migraciones de base de datos:

```bash
alembic upgrade head
```

4. Iniciar la aplicación:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Abrir documentación en el navegador:

- Swagger: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

### Ejecutar pruebas

```bash
pytest -q
```

### Ejemplos de llamadas API

Crear usuario:

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jdoe",
    "email": "jdoe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "active": true
  }'
```

Obtener lista de usuarios:

```bash
curl http://localhost:8000/users
```

Obtener usuario por ID:

```bash
curl http://localhost:8000/users/1
```

Actualizar usuario:

```bash
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "role": "admin"}'
```

Eliminar usuario:

```bash
curl -X DELETE http://localhost:8000/users/1
```

## Implementación con MySQL

La aplicación ahora utiliza MySQL como motor de base de datos. La configuración se controla con las siguientes variables de entorno:

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `DATABASE_URL` (opcional, si se prefiere usar una cadena completa)

Si `DATABASE_URL` está presente, se utiliza en lugar de las variables individuales.

### Ejemplo de configuración local

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=secret
export MYSQL_DATABASE=test_latam
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Notas

- Se usa `PyMySQL` como driver para MySQL.
- El archivo `requirements.txt` se ha actualizado para incluir `PyMySQL`.
- El `Dockerfile` mantiene la instalación estándar ya que no requiere paquetes adicionales para `PyMySQL`.

### Despliegue en GCP

El archivo `cloudbuild.yaml` construye la imagen Docker, ejecuta las pruebas y despliega la aplicación a Cloud Run.

Asegúrate de configurar estas variables en el entorno de Cloud Build:

- `PROJECT_ID`
- `REGION`

```bash
gcloud builds submit --config cloudbuild.yaml .
```
