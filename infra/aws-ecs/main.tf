data "aws_vpc" "default" { default = true }
data "aws_subnets" "default" {
  filter { name = "vpc-id", values = [data.aws_vpc.default.id] }
}
resource "aws_ecr_repository" "app" {
  name = var.project_name
  image_scanning_configuration { scan_on_push = true }
  force_delete = true
}
resource "aws_ecs_cluster" "main" { name = var.project_name }
resource "aws_iam_role" "task_execution" {
  name = "${var.project_name}-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}
resource "aws_iam_role_policy_attachment" "execution" {
  role = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_security_group" "alb" {
  name = "${var.project_name}-alb"
  vpc_id = data.aws_vpc.default.id
  ingress { from_port = 80, to_port = 80, protocol = "tcp", cidr_blocks = [var.allowed_cidr] }
  egress { from_port = 0, to_port = 0, protocol = "-1", cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_security_group" "task" {
  name = "${var.project_name}-task"
  vpc_id = data.aws_vpc.default.id
  ingress { from_port = 8000, to_port = 8000, protocol = "tcp", security_groups = [aws_security_group.alb.id] }
  egress { from_port = 0, to_port = 0, protocol = "-1", cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_lb" "app" {
  name = substr(var.project_name, 0, 25)
  load_balancer_type = "application"
  subnets = slice(data.aws_subnets.default.ids, 0, 2)
  security_groups = [aws_security_group.alb.id]
}
resource "aws_lb_target_group" "app" {
  name = substr("${var.project_name}-tg", 0, 32)
  port = 8000
  protocol = "HTTP"
  vpc_id = data.aws_vpc.default.id
  target_type = "ip"
  health_check { path = "/health", matcher = "200" }
}
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port = 80
  protocol = "HTTP"
  default_action { type = "forward", target_group_arn = aws_lb_target_group.app.arn }
}
resource "aws_ecs_task_definition" "app" {
  family = var.project_name
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = "512"
  memory = "1024"
  execution_role_arn = aws_iam_role.task_execution.arn
  container_definitions = jsonencode([{
    name = "api", image = var.image_uri, essential = true,
    portMappings = [{ containerPort = 8000, hostPort = 8000, protocol = "tcp" }],
    environment = [{ name = "DATABASE_URL", value = "sqlite:///./mediqueue.db" }, { name = "DEMO_SEED", value = "true" }],
    healthCheck = { command = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\""], interval = 30, timeout = 5, retries = 3, startPeriod = 20 }
  }])
}
resource "aws_ecs_service" "app" {
  name = var.project_name
  cluster = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
    subnets = slice(data.aws_subnets.default.ids, 0, 2)
    security_groups = [aws_security_group.task.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name = "api"
    container_port = 8000
  }
  depends_on = [aws_lb_listener.http, aws_iam_role_policy_attachment.execution]
}
