from chains.generate_prompt_chain import generate_style_prompt


def build_generate_prompt(style: str) -> str:
	return generate_style_prompt(style)