{{ if .Values.enabled }}

{{ template "tango-util.configuration.tpl" . }}

{{ $default_tango_host := printf "%s-%s" "databaseds-tango-base-" .Release.Name }}
{{ $tango_host := tpl (coalesce .Values.global.tango_host .Values.tango_host $default_tango_host | toString) . }}
{{ $dsconfig := coalesce .Values.global.dsconfig .Values.dsconfig}}
{{ $itango := coalesce .Values.global.itango .Values.itango}}
{{ $tangodb := coalesce .Values.global.tangodb .Values.tangodb}}
---

apiVersion: batch/v1
kind: Job
metadata:
  name: configure-alarm-{{ template "tmc-mid.name" . }}-{{ .Release.Name }}
  namespace: {{ .Release.Namespace }}
  labels:
{{ toYaml (coalesce .Values.global.labels .Values.labels "label:none") | indent 4 }}
  annotations:
{{ toYaml (coalesce .Values.global.annotations .Values.annotations "annotations:none") | indent 4 }}
spec:
  ttlSecondsAfterFinished: 100
  template:
    spec:
      volumes:
      - name: configure-alarrm
        configMap:
          name: "tm-alarmhandler-{{ template "tmc-mid.name" . }}-{{ .Release.Name }}"
      initContainers:
        - name: wait-for-devices
          image: "nexus.engageska-portugal.pt/tango-example/tmalarmhandler"
          imagePullPolicy: Always
          command:
            - sh
          args:
            - -c
            - "retry --max=20 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_subarray01 && \
              retry --max=20 -- tango_admin --ping-device ska_mid/tm_alarmhandler/tmalarmhandler"
          env:
          - name: TANGO_HOST
            value: {{ $tango_host }}
      containers:
      - name: configure-alarm
        image: "nexus.engageska-portugal.pt/tango-example/tmalarmhandler"
        imagePullPolicy: Always
        command:    
          - sh
        args:
          - -c
          - "/venv/bin/python data/configure-alarm.py "
        env:
        - name: TANGO_HOST
          value: {{ $tango_host }}
        volumeMounts:
          - name: configure-alarm
            mountPath: /app/data
            readOnly: true
      restartPolicy: OnFailure
{{ end }}

