
pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Project') {
            steps {
                sh '''
                    set -eu
                    test -f run.py
                    test -f requirements.txt
                    test -d expense_tracker
                    test -d tests
                    echo "Project files verified."
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    set -eu
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt
                    .venv/bin/pip install pytest
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    set -eu
                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Verify Azure Deployment') {
            steps {
                sh '''
                    set -eu
                    curl --fail --silent --show-error \
                        http://127.0.0.1/ -o /dev/null
                    echo "Deployed homepage is responding."

                    curl --fail --silent --show-error \
                        http://127.0.0.1/health
                    echo
                    echo "Health endpoint is responding."
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: checkout, tests and deployment checks passed.'
        }
        failure {
            echo 'FAILED: inspect the first error in Console Output.'
        }
    }
}
