FROM waggle/plugin-base:1.1.1-base

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py", "--process 1"]
