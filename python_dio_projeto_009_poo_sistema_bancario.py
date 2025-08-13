import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

"""
CLASSE CLIENTE
Representa um cliente genérico do banco
"""
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco  # Endereço do cliente
        self.contas = []  # Lista de contas do cliente

    # Método para realizar uma transação em uma conta
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    # Método para adicionar uma nova conta ao cliente
    def adicionar_conta(self, conta):
        self.contas.append(conta)

"""
CLASSE PESSOA FÍSICA
Herda de Cliente e representa um cliente pessoa física
"""
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)  # Chama o construtor da classe pai
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf  # Cadastro de Pessoa Física (identificador único)

"""
CLASSE CONTA
Representa uma conta bancária genérica
"""
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0  # Saldo inicial (privado)
        self._numero = numero  # Número da conta (privado)
        self._agencia = "0001"  # Agência padrão (privado)
        self._cliente = cliente  # Cliente dono da conta (privado)
        self._historico = Historico()  # Histórico de transações

    # Método de classe para criar nova conta
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    # Propriedades para acesso controlado aos atributos privados
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    # Método para realizar saque
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    # Método para realizar depósito
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True

"""
CLASSE CONTA CORRENTE
Herda de Conta e representa uma conta corrente específica
"""
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)  # Chama construtor da classe pai
        self._limite = limite  # Limite de saque
        self._limite_saques = limite_saques  # Número máximo de saques

    # Sobrescreve o método sacar com regras específicas da conta corrente
    def sacar(self, valor):
        # Conta quantos saques já foram realizados
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    # Método para representação em string da conta
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

"""
CLASSE HISTÓRICO
Registra o histórico de transações de uma conta
"""
class Historico:
    def __init__(self):
        self._transacoes = []  # Lista de transações (privado)

    @property
    def transacoes(self):
        return self._transacoes

    # Adiciona uma nova transação ao histórico
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,  # Nome da classe da transação
                "valor": transacao.valor,  # Valor da transação
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),  # Data formatada
            }
        )

"""
CLASSE ABSTRATA TRANSAÇÃO
Define a interface para transações bancárias
"""
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

"""
CLASSE SAQUE
Implementa uma transação de saque
"""
class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor  # Valor do saque

    @property
    def valor(self):
        return self._valor

    # Registra o saque na conta
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

"""
CLASSE DEPÓSITO
Implementa uma transação de depósito
"""
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor  # Valor do depósito

    @property
    def valor(self):
        return self._valor

    # Registra o depósito na conta
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

"""
FUNÇÕES DE INTERFACE DO USUÁRIO
"""

# Exibe o menu principal e obtém a opção do usuário
def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

# Filtra cliente por CPF
def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

# Recupera a conta de um cliente (atualmente só retorna a primeira conta)
def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

# Operação de depósito
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

# Operação de saque
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

# Operação de extrato
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

# Cria um novo cliente
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")

# Cria uma nova conta
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")

# Lista todas as contas
def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

# Função principal que gerencia o fluxo do programa
def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


# Ponto de entrada do programa
if __name__ == "__main__":
    main()