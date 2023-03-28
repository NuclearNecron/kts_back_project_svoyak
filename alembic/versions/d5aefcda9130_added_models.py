"""added models

Revision ID: d5aefcda9130
Revises: 
Create Date: 2023-03-25 21:31:33.192473

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d5aefcda9130"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "admin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "player",
        sa.Column("tg_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("tg_id"),
        sa.UniqueConstraint("tg_id"),
    )
    op.create_table(
        "game",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.Integer(), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("winner", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column(
            "RemainingQuestions", postgresql.ARRAY(sa.Integer()), nullable=True
        ),
        sa.ForeignKeyConstraint(["winner"], ["admin.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "questionpack",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("admin", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["admin"], ["admin.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "gamescore",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("player", sa.Integer(), nullable=False),
        sa.Column("game", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("right_answers", sa.Integer(), nullable=False),
        sa.Column("wrong_answers", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game"], ["game.id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(
            ["player"], ["player.tg_id"], ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "round",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("pack", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["pack"], ["questionpack.id"], ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "theme",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["round"], ["round.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "question",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("theme", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["theme"], ["theme.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("question", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question"], ["question.id"], ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("answers")
    op.drop_table("question")
    op.drop_table("theme")
    op.drop_table("round")
    op.drop_table("gamescore")
    op.drop_table("questionpack")
    op.drop_table("game")
    op.drop_table("player")
    op.drop_table("admin")
    # ### end Alembic commands ###
