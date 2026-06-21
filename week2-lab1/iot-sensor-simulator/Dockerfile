FROM python:3.11-slim
#dung imgae Python 3.11 (phien ban slim) lam nen tang, moi lenh phia sau de chay tren moi truong nay
WORKDIR /app
#dat thu muc lam viec ben trong container la /app. Tat ca lenh copy, run, cmd sau do deu thuc thi tai day
#neu /app chua ton tai, Docker tu tao ra no
COPY requirements.txt .
#copy file requirements.txt tu may host vao thuc muc hien tai trong container (/app/requirements.txt)
#dau . la viet tat cua workdir
RUN pip install --no-cache-dir -r requirements.txt
#cai cai thu vien python duoc liet ke trong requirements.txt
COPY app.py .
#dung copy . . de copy toan bo file tu thu muc hien tao vao container
#copy file app.py vao /app/app.py 
CMD ["python", "app.py"]
#lenh mac dinh khi container khoi chay: chay python app.py
#nên tạo file .dockerignore để loại trừ các file không cần thiết khi dùng copy . .:
#__pycache__/ *.pyc .env .git
