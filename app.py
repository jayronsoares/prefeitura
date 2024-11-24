from flask import Flask, render_template, request, redirect, url_for, flash
import os
import psycopg2
from psycopg2 import sql, Error
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # For flash messages

# Configure logging
logging.basicConfig(level=logging.ERROR, filename="app.log",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# PostgreSQL Connection Configuration
def connect_postgres():
    try:
        connection = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DATABASE')
        )
        return connection
    except Error as e:
        logging.error(f"Erro na conexão com o banco de dados: {e}")
        return None


# Route to handle form submission and insert data
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # Render the form page

@app.route('/enviar', methods=['POST'])
def enviar_formulario():
    try:
        # Getting form data
        nome = request.form['nome']
        idade = request.form['idade']
        rua = request.form['rua']
        bairro = request.form['bairro']
        cep = request.form['cep']
        celular = request.form['celular']
        cpf = request.form['cpf']
        tipo_reclamacao = request.form['tipo_reclamacao']
        detalhes_reclamacao = request.form['detalhes_reclamacao']

        # Validate if the data matches the required formats (in case JavaScript doesn't work)
        if not all([nome, idade, rua, bairro, cep, celular, cpf, tipo_reclamacao, detalhes_reclamacao]):
            flash("Por favor, preencha todos os campos.", "error")
            return redirect(url_for('index'))

        # Insert data into PostgreSQL
        connection = connect_postgres()
        if connection:
            cursor = connection.cursor()
            insert_query = sql.SQL("""
                INSERT INTO reclamacao 
                (nome, idade, rua, bairro, cep, celular, cpf, tipo_reclamacao, detalhes_reclamacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
            cursor.execute(insert_query, (nome, idade, rua, bairro, cep, celular, cpf, tipo_reclamacao, detalhes_reclamacao))
            connection.commit()

            cursor.close()
            connection.close()

            # Redirect to success page
            return render_template('sucesso.html', message="Sua reclamação foi enviada com sucesso!")

    except Exception as e:
        logging.error(f"Erro ao processar o formulário: {e}")
        flash("Ocorreu um erro. Tente novamente.", "error")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
