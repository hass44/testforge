"""Matched-FLOPs accounting for transformer training compute."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransformerConfig:
    name: str
    hidden_size: int
    intermediate_size: int
    num_hidden_layers: int
    num_attention_heads: int
    num_key_value_heads: int
    head_dim: int
    vocab_size: int
    mlp_gateup_matrices: int = 2
    tie_word_embeddings: bool = False

    @property
    def q_dim(self) -> int:
        return self.num_attention_heads * self.head_dim

    @property
    def kv_dim(self) -> int:
        return self.num_key_value_heads * self.head_dim

    def attention_params_per_layer(self) -> int:
        d = self.hidden_size
        return d * self.q_dim + 2 * d * self.kv_dim + self.q_dim * d

    def mlp_params_per_layer(self) -> int:
        d, i = self.hidden_size, self.intermediate_size
        return self.mlp_gateup_matrices * d * i + i * d

    def non_embedding_params(self) -> int:
        per_layer = self.attention_params_per_layer() + self.mlp_params_per_layer()
        return self.num_hidden_layers * per_layer

    def embedding_params(self) -> int:
        if self.tie_word_embeddings:
            return self.vocab_size * self.hidden_size
        return 2 * self.vocab_size * self.hidden_size

    def total_params(self) -> int:
        return self.non_embedding_params() + self.embedding_params()

    def _proj_flops_per_token(self) -> int:
        per_layer = self.attention_params_per_layer() + self.mlp_params_per_layer()
        return 2 * self.num_hidden_layers * per_layer

    def _attn_flops_per_token(self, seq_len: int, bidirectional: bool) -> float:
        frac = 1.0 if bidirectional else 0.5
        return 2 * self.num_hidden_layers * (2 * seq_len * self.q_dim) * frac

    def _lm_head_flops_per_token(self) -> int:
        return 2 * self.hidden_size * self.vocab_size

    def forward_flops_per_token(self, seq_len: int, bidirectional: bool) -> float:
        return (
            self._proj_flops_per_token()
            + self._attn_flops_per_token(seq_len, bidirectional)
            + self._lm_head_flops_per_token()
        )

    def training_flops_per_token(self, seq_len: int, bidirectional: bool) -> float:
        return 3.0 * self.forward_flops_per_token(seq_len, bidirectional)

    def total_training_flops(
        self, n_tokens: int, seq_len: int, bidirectional: bool
    ) -> float:
        return n_tokens * self.training_flops_per_token(seq_len, bidirectional)

    def approx_6nd(self, n_tokens: int) -> float:
        return 6.0 * self.non_embedding_params() * n_tokens


@dataclass
class FlopsBudget:
    config: TransformerConfig
    seq_len: int
    bidirectional: bool
    total_flops: float = 0.0
    total_tokens: int = 0
    steps: int = 0

    def step(self, batch_tokens: int) -> None:
        self.total_flops += self.config.total_training_flops(
            batch_tokens, self.seq_len, self.bidirectional
        )
        self.total_tokens += batch_tokens
        self.steps += 1

    def flops_for_tokens(self, n_tokens: int) -> float:
        return self.config.total_training_flops(
            n_tokens, self.seq_len, self.bidirectional
        )

    def tokens_for_flops(self, target_flops: float) -> int:
        per_token = self.config.training_flops_per_token(
            self.seq_len, self.bidirectional
        )
        return int(target_flops / per_token)


def matched_token_counts(
    config: TransformerConfig, seq_len: int, target_flops: float
) -> dict[str, int]:
    ar = FlopsBudget(config, seq_len, bidirectional=False)
    diff = FlopsBudget(config, seq_len, bidirectional=True)
    return {
        "ar_tokens": ar.tokens_for_flops(target_flops),
        "diffusion_tokens": diff.tokens_for_flops(target_flops),
    }
