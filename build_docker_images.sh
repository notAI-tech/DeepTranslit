rm fastDeploy.py
wget https://raw.githubusercontent.com/notAI-tech/fastDeploy/master/cli/fastDeploy.py

python fastDeploy.py --build temp --source_dir fastDeploy_recipe  --verbose --base tf_1_14_cpu --extra_config '{"LANG": "hindi", "BATCH_SIZE": "4"}'
docker commit temp notaitech/deeptranslit:hindi
docker push notaitech/deeptranslit:hindi

python fastDeploy.py --build temp --source_dir fastDeploy_recipe  --verbose --base tf_1_14_cpu --extra_config '{"LANG": "telugu", "BATCH_SIZE": "4"}'
docker commit temp notaitech/deeptranslit:telugu
docker push notaitech/deeptranslit:telugu

python fastDeploy.py --build temp --source_dir fastDeploy_recipe  --verbose --base tf_1_14_cpu --extra_config '{"LANG": "kannada", "BATCH_SIZE": "4"}'
docker commit temp notaitech/deeptranslit:kannada
docker push notaitech/deeptranslit:kannada

python fastDeploy.py --build temp  --source_dir fastDeploy_recipe  --verbose --base tf_1_14_cpu --extra_config '{"LANG": "tamil", "BATCH_SIZE": "4"}'
docker commit temp notaitech/deeptranslit:tamil
docker push notaitech/deeptranslit:tamil

python fastDeploy.py --build temp --source_dir fastDeploy_recipe  --verbose --base tf_1_14_cpu --extra_config '{"LANG": "malayalam", "BATCH_SIZE": "4"}'
docker commit temp notaitech/deeptranslit:malayalam
docker push notaitech/deeptranslit:malayalam

python fastDeploy.py --build temp --source_dir fastDeploy_recipe  --verbose --base tf_1_14_cpu --extra_config '{"LANG": "marathi", "BATCH_SIZE": "4"}'
docker commit temp notaitech/deeptranslit:marathi
docker push notaitech/deeptranslit:marathi
