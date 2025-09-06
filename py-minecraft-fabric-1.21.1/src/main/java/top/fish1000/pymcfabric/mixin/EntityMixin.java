package top.fish1000.pymcfabric.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.injection.At;

import net.minecraft.entity.Entity;
import net.minecraft.util.ActionResult;
import top.fish1000.pymcfabric.PymcMngr;

@Mixin(Entity.class)
public abstract class EntityMixin {

    private void tick(String action) {
        PymcMngr.tick("entity " + action, ((Entity) (Object) this));
        PymcMngr.tick("entity " + action + ' ' + ((Entity) (Object) this).getName().getString(),
                ((Entity) (Object) this));
        PymcMngr.tick("entity " + action + ' ' + ((Entity) (Object) this).getUuidAsString(), ((Entity) (Object) this));
    }

    @Inject(method = "interact(Lnet/minecraft/entity/player/PlayerEntity;Lnet/minecraft/util/Hand;)Lnet/minecraft/util/ActionResult;", at = @At("HEAD"))
    private void entityInteract(CallbackInfoReturnable<ActionResult> info) {
        tick("interact");
    }

    @Inject(method = "tick()V", at = @At("HEAD"))
    private void entityTick(CallbackInfo info) {
        tick("tick");
    }

    @Inject(method = "setRemoved(Lnet/minecraft/entity/Entity$RemovalReason;)V", at = @At("HEAD"))
    private void entityRemoved(CallbackInfo info) {
        tick("removed");
    }
}
