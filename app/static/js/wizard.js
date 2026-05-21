document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-wizard-form]");
  if (!form) {
    return;
  }

  const panes = Array.from(document.querySelectorAll("[data-step-pane]"));
  const stepButtons = Array.from(document.querySelectorAll("[data-step-button]"));
  const progressBar = document.querySelector("[data-wizard-progress]");
  const progressLabel = document.querySelector("[data-wizard-progress-label]");
  const prevButton = document.querySelector("[data-wizard-prev]");
  const nextButton = document.querySelector("[data-wizard-next]");
  const finishButton = document.querySelector("[data-wizard-finish]");
  const fillExampleButton = document.querySelector("[data-wizard-fill-example]");
  const reviewModalElement = document.getElementById("wizardReviewModal");
  const reviewModal = reviewModalElement ? new bootstrap.Modal(reviewModalElement) : null;
  const totalSteps = panes.length;

  let currentStep = 0;
  let loadingTimer = null;

  const loadingMask = document.createElement("div");
  loadingMask.className = "wizard-loading-mask";
  loadingMask.innerHTML = `
    <div class="wizard-loading-card">
      <div class="wizard-loading-spinner"></div>
      <div class="fw-semibold mb-1">Atualizando etapa</div>
      <div class="text-secondary small">Transição suave para testar o fluxo do wizard.</div>
    </div>
  `;
  form.style.position = "relative";
  form.prepend(loadingMask);

  // Validação real será implementada futuramente no backend; aqui só reproduzimos feedback visual.
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((element) => new bootstrap.Tooltip(element));

  const updateProgress = () => {
    const percentage = ((currentStep + 1) / totalSteps) * 100;
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
    }
    if (progressLabel) {
      progressLabel.textContent = `Etapa ${currentStep + 1} de ${totalSteps}`;
    }
  };

  const setButtonStates = () => {
    if (prevButton) {
      prevButton.disabled = currentStep === 0;
    }
    if (nextButton) {
      nextButton.classList.toggle("d-none", currentStep === totalSteps - 1);
    }
    if (finishButton) {
      finishButton.classList.toggle("d-none", currentStep !== totalSteps - 1);
    }
    stepButtons.forEach((button, index) => {
      button.classList.toggle("is-active", index === currentStep);
    });
  };

  const removeTransientValidation = (field) => {
    window.setTimeout(() => {
      field.classList.remove("wizard-pulse-invalid");
      if (!field.matches(":checked") && !field.value) {
        field.classList.remove("is-invalid");
      }
    }, 1200);
  };

  const simulateValidationVisuals = (pane) => {
    const candidates = Array.from(pane.querySelectorAll("[data-simulate-field]"));
    let highlighted = 0;

    candidates.forEach((field) => {
      const empty = field.type === "checkbox" ? !field.checked : !field.value;
      if (!empty || highlighted >= 3) {
        return;
      }

      field.classList.add("is-invalid", "wizard-pulse-invalid");
      highlighted += 1;
      removeTransientValidation(field);
    });
  };

  const showMask = () => {
    loadingMask.classList.add("is-visible");
    if (loadingTimer) {
      window.clearTimeout(loadingTimer);
    }
  };

  const hideMask = () => {
    loadingTimer = window.setTimeout(() => loadingMask.classList.remove("is-visible"), 180);
  };

  const showStep = (targetStep) => {
    const nextStep = Math.max(0, Math.min(targetStep, totalSteps - 1));
    panes.forEach((pane, index) => {
      pane.classList.toggle("is-active", index === nextStep);
      pane.setAttribute("aria-hidden", String(index !== nextStep));
    });
    currentStep = nextStep;
    updateProgress();
    setButtonStates();
    updateReviewSummary();
    const activePane = panes[currentStep];
    if (activePane) {
      activePane.scrollIntoView({ behavior: "smooth", block: "start" });
      simulateValidationVisuals(activePane);
    }
  };

  const transitionTo = (targetStep) => {
    showMask();
    window.setTimeout(() => {
      showStep(targetStep);
      hideMask();
    }, 160);
  };

  const setTextareaHeight = (textarea) => {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  const initTextareas = () => {
    form.querySelectorAll("[data-autoresize]").forEach((textarea) => {
      setTextareaHeight(textarea);
      textarea.addEventListener("input", () => setTextareaHeight(textarea));
    });
  };

  const formatPhone = (value) => {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    if (digits.length <= 10) {
      return digits.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{4})(\d)/, "$1-$2");
    }
    return digits.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{5})(\d)/, "$1-$2");
  };

  const initMasks = () => {
    form.querySelectorAll('[data-mask="phone"]').forEach((field) => {
      field.addEventListener("input", () => {
        field.value = formatPhone(field.value);
      });
    });
  };

  const updateConditionalVisibility = () => {
    form.querySelectorAll("[data-conditional-select]").forEach((select) => {
      const targetId = select.getAttribute("data-conditional-select");
      const target = document.getElementById(`${targetId}_wrap`);
      if (!target) {
        return;
      }
      target.classList.toggle("d-none", select.value !== "outro");
    });

    form.querySelectorAll("[data-conditional-switch]").forEach((toggle) => {
      const targetId = toggle.getAttribute("data-conditional-target");
      if (!targetId) {
        return;
      }
      const target = document.getElementById(targetId);
      if (!target) {
        return;
      }
      target.classList.toggle("d-none", !toggle.checked);
    });
  };

  const bindConditionalControls = () => {
    form.querySelectorAll("[data-conditional-select]").forEach((select) => {
      select.addEventListener("change", updateConditionalVisibility);
    });
    form.querySelectorAll("[data-conditional-switch]").forEach((toggle) => {
      toggle.addEventListener("change", updateConditionalVisibility);
    });
    updateConditionalVisibility();
  };

  const buildExpenseRow = (index) => `
    <tr data-row-template="expense">
      <td><input type="text" class="form-control form-control-sm" name="despesas_atividade[${index}][item_despesa]" placeholder="Ex.: combustível" data-field="item_despesa"></td>
      <td><input type="text" class="form-control form-control-sm" name="despesas_atividade[${index}][tipo]" placeholder="Tipo" data-field="tipo"></td>
      <td><input type="number" class="form-control form-control-sm" name="despesas_atividade[${index}][quantidade]" placeholder="0" min="0" step="0.1" data-field="quantidade"></td>
      <td><input type="text" class="form-control form-control-sm" name="despesas_atividade[${index}][unidade]" placeholder="kg, litro..." data-field="unidade"></td>
      <td><input type="number" class="form-control form-control-sm" name="despesas_atividade[${index}][custo_reais]" placeholder="0,00" min="0" step="0.01" data-field="custo_reais"></td>
      <td><input type="text" class="form-control form-control-sm" name="despesas_atividade[${index}][outros]" placeholder="Observações" data-field="outros"></td>
      <td><select class="form-select form-select-sm" name="despesas_atividade[${index}][frequencia]" data-field="frequencia"><option value="">Selecione</option><option value="diaria">Diária</option><option value="semanal">Semanal</option><option value="mensal">Mensal</option><option value="anual">Anual</option></select></td>
      <td class="text-end"><button type="button" class="btn btn-outline-danger btn-sm" data-remove-row><i class="bi bi-trash3"></i></button></td>
    </tr>`;

  const buildFishRow = (index) => `
    <tr data-row-template="fish">
      <td><input type="text" class="form-control form-control-sm" name="pescados_safra[${index}][nome_comum]" placeholder="Ex.: tainha" data-field="nome_comum"></td>
      <td><input type="text" class="form-control form-control-sm" name="pescados_safra[${index}][inicio_safra]" placeholder="Jan" data-field="inicio_safra"></td>
      <td><input type="text" class="form-control form-control-sm" name="pescados_safra[${index}][fim_safra]" placeholder="Mar" data-field="fim_safra"></td>
      <td class="text-end"><button type="button" class="btn btn-outline-danger btn-sm" data-remove-row><i class="bi bi-trash3"></i></button></td>
    </tr>`;

  const renumberRows = (tbody, prefix) => {
    Array.from(tbody.querySelectorAll("tr")).forEach((row, index) => {
      row.querySelectorAll("[data-field]").forEach((field) => {
        const fieldName = field.getAttribute("data-field");
        field.name = `${prefix}[${index}][${fieldName}]`;
      });
    });
  };

  const initDynamicTables = () => {
    const expensesBody = document.querySelector("[data-expenses-body]");
    const fishBody = document.querySelector("[data-fish-body]");
    const addExpenseButton = document.querySelector("[data-add-expense]");
    const addFishButton = document.querySelector("[data-add-fish]");

    if (expensesBody && expensesBody.children.length === 0) {
      expensesBody.insertAdjacentHTML("beforeend", buildExpenseRow(0));
    }
    if (fishBody && fishBody.children.length === 0) {
      fishBody.insertAdjacentHTML("beforeend", buildFishRow(0));
    }

    addExpenseButton?.addEventListener("click", () => {
      expensesBody.insertAdjacentHTML("beforeend", buildExpenseRow(expensesBody.children.length));
      renumberRows(expensesBody, "despesas_atividade");
    });

    addFishButton?.addEventListener("click", () => {
      fishBody.insertAdjacentHTML("beforeend", buildFishRow(fishBody.children.length));
      renumberRows(fishBody, "pescados_safra");
    });

    [expensesBody, fishBody].forEach((tbody) => {
      if (!tbody) {
        return;
      }
      tbody.addEventListener("click", (event) => {
        const removeButton = event.target.closest("[data-remove-row]");
        if (!removeButton) {
          return;
        }
        const row = removeButton.closest("tr");
        if (!row) {
          return;
        }
        if (tbody.children.length === 1) {
          row.querySelectorAll("input, select").forEach((field) => {
            if (field.type === "checkbox") {
              field.checked = false;
            } else {
              field.value = "";
            }
          });
          return;
        }
        row.remove();
        renumberRows(tbody, tbody === expensesBody ? "despesas_atividade" : "pescados_safra");
      });
    });
  };

  const getFieldValue = (selector) => {
    const field = form.querySelector(selector);
    return field ? field.value.trim() : "";
  };

  const getCheckedLabels = (selector) => {
    return Array.from(form.querySelectorAll(selector))
      .filter((field) => field.checked)
      .map((field) => {
        const label = form.querySelector(`label[for="${field.id}"]`);
        return label ? label.textContent.trim() : field.value;
      });
  };

  const countRows = (tbodySelector) => {
    const tbody = document.querySelector(tbodySelector);
    return tbody ? tbody.querySelectorAll("tr").length : 0;
  };

  const updateSummaryChipList = (container, items) => {
    if (!container) {
      return;
    }
    container.innerHTML = "";
    const filtered = items.filter(Boolean);
    if (filtered.length === 0) {
      container.innerHTML = '<span class="badge text-bg-light text-secondary border">Nenhuma seleção múltipla registrada ainda</span>';
      return;
    }
    filtered.forEach((item) => {
      const chip = document.createElement("span");
      chip.className = "badge text-bg-primary-subtle text-primary border";
      chip.textContent = item;
      container.appendChild(chip);
    });
  };

  const updateReviewSummary = () => {
    const summaryColeta = document.getElementById("summaryColeta");
    const summaryColetaExtra = document.getElementById("summaryColetaExtra");
    const summaryPessoa = document.getElementById("summaryPessoa");
    const summaryPessoaExtra = document.getElementById("summaryPessoaExtra");
    const summarySaude = document.getElementById("summarySaude");
    const summarySaudeExtra = document.getElementById("summarySaudeExtra");
    const summaryAtividade = document.getElementById("summaryAtividade");
    const summaryAtividadeExtra = document.getElementById("summaryAtividadeExtra");
    const summaryEmbarcacao = document.getElementById("summaryEmbarcacao");
    const summaryEmbarcacaoExtra = document.getElementById("summaryEmbarcacaoExtra");
    const summaryTabelas = document.getElementById("summaryTabelas");
    const summaryTabelasExtra = document.getElementById("summaryTabelasExtra");
    const summaryChips = document.getElementById("summaryChips");

    const nome = getFieldValue('[name="nome"]') || "Sem nome ainda";
    const municipio = getFieldValue('[name="municipio"]') || "Município não definido";
    const coletor = getFieldValue('[name="coletor"]') || "Coletor não definido";
    const dataColeta = getFieldValue('[name="data_coleta"]') || "--";
    const sexo = getFieldValue('[name="sexo"]') || "--";
    const atividade = getFieldValue('[name="categoria_pesca"]') || "--";
    const horas = getFieldValue('[name="horas_trabalho_dia"]') || "--";
    const rendaMensal = getFieldValue('[name="renda_media_mensal"]') || "--";
    const statusFinanceiro = getFieldValue('[name="status_financeiro"]') || "--";
    const embarcacao = getFieldValue('[name="nome_embarcacao"]') || "Sem embarcação definida";

    if (summaryColeta) {
      summaryColeta.textContent = `${municipio} • ${coletor}`;
    }
    if (summaryColetaExtra) {
      summaryColetaExtra.textContent = `Código: ${getFieldValue('[name="codigo_coleta"]') || '--'} | Data: ${dataColeta}`;
    }
    if (summaryPessoa) {
      summaryPessoa.textContent = nome;
    }
    if (summaryPessoaExtra) {
      summaryPessoaExtra.textContent = `Sexo: ${sexo} | Naturalidade: ${getFieldValue('[name="naturalidade"]') || '--'}`;
    }
    if (summarySaude) {
      summarySaude.textContent = getCheckedLabels('input[type="checkbox"][name^="problema_"]').join(', ') || 'Sem alertas marcados';
    }
    if (summarySaudeExtra) {
      const registros = [
        getCheckedLabels('[name="registro_inss"]'),
        getCheckedLabels('[name="registro_colonia"]'),
        getCheckedLabels('[name="registro_associacao"]'),
        getCheckedLabels('[name="possui_carteira_pescador"]'),
      ];
      summarySaudeExtra.textContent = `Registros visuais: ${registros.flat().length ? 'ativados' : 'não ativados'}`;
    }
    if (summaryAtividade) {
      summaryAtividade.textContent = `${atividade} • ${horas} h/dia`;
    }
    if (summaryAtividadeExtra) {
      summaryAtividadeExtra.textContent = `Renda mensal: ${rendaMensal} | Dias embarcado: ${getFieldValue('[name="media_dias_embarcado"]') || '--'}`;
    }
    if (summaryEmbarcacao) {
      summaryEmbarcacao.textContent = `${embarcacao} • ${statusFinanceiro}`;
    }
    if (summaryEmbarcacaoExtra) {
      summaryEmbarcacaoExtra.textContent = `Propulsão: ${getCheckedLabels('input[name="tipo_propulsao[]"]:checked').join(', ') || '--'}`;
    }
    if (summaryTabelas) {
      summaryTabelas.textContent = `${countRows('[data-expenses-body]')} despesas e ${countRows('[data-fish-body]')} safras`;
    }
    if (summaryTabelasExtra) {
      summaryTabelasExtra.textContent = 'Linhas podem ser adicionadas e removidas livremente nesta interface.';
    }

    updateSummaryChipList(summaryChips, [
      ...getCheckedLabels('[name="relacao_trabalho[]"]:checked'),
      ...getCheckedLabels('input[name="tipo_propulsao[]"]:checked'),
    ]);
  };

  const fillExampleData = () => {
    const values = {
      codigo_coleta: 'CLT-2026-001',
      codigo_foto: 'IMG-2048',
      municipio: 'Bragança',
      localidade: 'Comunidade do Amapá',
      coletor: 'Ana Souza',
      data_coleta: '2026-05-21',
      digitador: 'Diego Alves',
      data_digitacao: '2026-05-21',
      observacoes: 'Exemplo de preenchimento para validação visual.',
      nome: 'João da Silva',
      apelido: 'João da Rede',
      telefone: '(91) 99999-9999',
      sexo: 'M',
      data_nascimento: '1987-03-18',
      naturalidade: 'Bragança - PA',
      estado_civil: 'Casado',
      atividade_principal_renda: 'Pesca artesanal',
      atividade_secundaria_renda: 'Bicos sazonais',
      composicao_familiar: '4',
      escolaridade: 'Ensino fundamental completo',
      local_moradia: 'outro',
      tipo_construcao: 'outro',
      outros_problemas: 'Nenhum no momento.',
      tempo_na_atividade: '17 anos',
      horas_trabalho_dia: '7.5',
      principais_fontes_renda_familiar: 'Pesca, venda direta e apoio familiar.',
      categoria_pesca: 'pescador_artesanal',
      principal_pescaria_pescado: 'Tainha',
      petrecho_nome: 'Rede de malha',
      petrecho_tamanho_metros: '120',
      petrecho_tamanho_bracas: '60',
      petrecho_unidades: '3',
      petrecho_material: 'Nylon',
      tipo_iscas: 'Camarão e sardinha',
      processo_lancamento_recolhimento: 'Lançamento ao amanhecer e recolhimento no fim da tarde.',
      quadrantes_mapa: 'Quadrantes próximos à costa leste.',
      media_dias_embarcado: '8',
      viagens_por_mes: '6',
      producao_media_viagem_kg: '48',
      producao_media_viagem_unidades: '120',
      valor_medio_kg_primeira_qualidade: '22.50',
      valor_medio_kg_segunda_qualidade: '16.00',
      valor_medio_kg_terceira_qualidade: '9.50',
      renda_media_mensal: '4200',
      renda_media_por_pescaria: '680',
      conservacao_pescado: 'Gelo em caixa térmica',
      proprietario_petrechos: 'Associação local',
      percepcao_pesca_passado: 'Melhor que o ano anterior',
      percepcao_tamanho_volume_capturado: 'Volume estável, peixe um pouco menor',
      status_financeiro: 'quitada',
      nome_proprietario: 'Marcos Oliveira',
      apelido_proprietario: 'Marquinhos',
      cilindros_hp: '18 HP',
      porto_origem: 'Porto do Cajueiro',
      porto_desembarque: 'Porto da Cidade',
      nome_embarcacao: 'Esperança do Mar',
      comprimento: '8.4',
      num_registro: 'REG-8892',
      largura: '2.1',
      tonelada_bruta_ab: '2.8',
      capacidade_tripulacao: '4',
      ano_construcao: '2019',
      tipo_embarcacao: 'Canoa motorizada',
      nome_colonia: 'Colônia Z-12',
      nome_associacao: 'Associação do Estuário',
      tipo_carteira: 'pequena_colonia',
      local_moradia_outro: 'Vila do Arraial',
      tipo_construcao_outro: 'Palafita',
    };

    Object.entries(values).forEach(([name, value]) => {
      const field = form.querySelector(`[name="${name}"]`);
      if (!field) {
        return;
      }
      field.value = value;
      field.dispatchEvent(new Event("input", { bubbles: true }));
      field.dispatchEvent(new Event("change", { bubbles: true }));
    });

    ["registro_inss", "registro_colonia", "registro_associacao", "possui_carteira_pescador", "pesca_embarcada", "embarcacao_propria", "registro_capitania", "registro_rgp", "licenciamento_ibama", "licenciamento_mpa"].forEach((name) => {
      const field = form.querySelector(`[name="${name}"]`);
      if (field) {
        field.checked = true;
        field.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });

    ["problema_vista", "problema_pele"].forEach((name) => {
      const field = form.querySelector(`[name="${name}"]`);
      if (field) {
        field.checked = true;
      }
    });

    ["relacao_trabalho[]", "tipo_propulsao[]"].forEach((name) => {
      form.querySelectorAll(`[name="${name}"]`).forEach((field, index) => {
        if (index === 0 || index === 1) {
          field.checked = true;
        }
      });
    });

    const expensesBody = document.querySelector("[data-expenses-body]");
    const fishBody = document.querySelector("[data-fish-body]");
    if (expensesBody) {
      expensesBody.innerHTML = buildExpenseRow(0) + buildExpenseRow(1);
      renumberRows(expensesBody, "despesas_atividade");
    }
    if (fishBody) {
      fishBody.innerHTML = buildFishRow(0) + buildFishRow(1);
      renumberRows(fishBody, "pescados_safra");
    }

    updateConditionalVisibility();
    updateReviewSummary();
  };

  stepButtons.forEach((button) => {
    button.addEventListener("click", () => transitionTo(Number(button.dataset.stepTarget)));
  });

  prevButton?.addEventListener("click", () => transitionTo(currentStep - 1));
  nextButton?.addEventListener("click", () => transitionTo(currentStep + 1));
  finishButton?.addEventListener("click", () => {
    updateReviewSummary();
    reviewModal?.show();
  });
  fillExampleButton?.addEventListener("click", fillExampleData);

  form.addEventListener("input", (event) => {
    const field = event.target;
    if (!(field instanceof HTMLElement)) {
      return;
    }
    if (field.classList.contains("is-invalid")) {
      field.classList.remove("is-invalid");
    }
    updateReviewSummary();
  });

  form.addEventListener("change", () => {
    updateConditionalVisibility();
    updateReviewSummary();
  });

  initTextareas();
  initMasks();
  bindConditionalControls();
  initDynamicTables();
  updateReviewSummary();
  setButtonStates();
  updateProgress();
});
