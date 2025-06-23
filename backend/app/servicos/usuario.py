from sqlalchemy.orm import Session
from typing import Optional
from ..modelos.usuario import Usuario
from ..esquemas.usuario import UsuarioCreate
from ..core.seguranca import criarHashSenha, verificarSenha

class UsuarioService:
    
    def criarUsuario(self, db: Session, dados_usuario: UsuarioCreate) -> Usuario:
        """Cria um novo usuário no sistema"""
        senha_hash = criarHashSenha(dados_usuario.senha)
        
        usuario_db = Usuario(
            email=dados_usuario.email,
            nome=dados_usuario.nome,
            cpf=dados_usuario.cpf,
            perfil=dados_usuario.perfil,
            senha_hash=senha_hash
        )
        
        db.add(usuario_db)
        db.commit()
        db.refresh(usuario_db)
        return usuario_db
    
    def obterUsuarioPorEmail(self, db: Session, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    def obterUsuarioPorId(self, db: Session, usuario_id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    def autenticarUsuario(self, db: Session, email: str, senha: str) -> Optional[Usuario]:
        """Autentica usuário verificando email e senha"""
        usuario = self.obterUsuarioPorEmail(db, email)
        
        if not usuario:
            return None
            
        if not verificarSenha(senha, usuario.senha_hash):
            return None
            
        return usuario
    
    def validarCpf(self, cpf: str) -> bool:
        """Valida formato básico do CPF"""
        if not cpf or len(cpf) != 11:
            return False
        
        # Verifica se não são todos os dígitos iguais
        if cpf == cpf[0] * 11:
            return False
            
        return True

# Instância do serviço
usuario_service = UsuarioService() 