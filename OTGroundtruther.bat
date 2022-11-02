cd %~dp0
cd ..
call venv\Scripts\activate
cd OTGroundTruther
python __main__.py
timeout /T 10