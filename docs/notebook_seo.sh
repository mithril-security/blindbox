#!/bin/sh
set -e  # Exit if any command fails

sed -i '/<head>/a <meta name="description" content="Quick tour of BlindBox: Secure deployment, Confidential VMs, and customizable access to protect SaaS user data.">' $READTHEDOCS_OUTPUT/html/docs/getting-started/quick-tour/index.html
sed -i '/<head>/a <meta name="description" content=""Create a confidential OpenAI Whisper API with FastAPI and BlindBox: Secure user data in deployment steps.">' $READTHEDOCS_OUTPUT/html/docs/how-to-guides/openai-whisper/index.html
sed -i '/<head>/a <meta name="description" content="Deploy a confidential Santacoder LLM API with FastAPI and BlindBox: Privacy-focused code generation and packaging.">' $READTHEDOCS_OUTPUT/html/docs/how-to-guides/santacoder/index.html
sed -i '/<head>/a <meta name="description" content="Prepare an application image for BlindBox: Learn packaging constraints and techniques for secure VM deployment.">' $READTHEDOCS_OUTPUT/html/docs/tutorials/prepare-app/index.html